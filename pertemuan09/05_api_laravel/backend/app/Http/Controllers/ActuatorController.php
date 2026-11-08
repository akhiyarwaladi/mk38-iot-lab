<?php

namespace App\Http\Controllers;

use App\Models\Actuator;
use App\Models\ActuatorCommand;
use App\Models\ActuatorStateEvent;
use App\Models\Device;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;

class ActuatorController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $data = $request->validate(['device_id' => ['nullable', 'string', 'max:40']]);
        return response()->json(Actuator::query()->when($data['device_id'] ?? null,
            fn ($q, $id) => $q->where('device_id', $id))->orderBy('id')->limit(100)->get());
    }

    public function register(Request $request): JsonResponse
    {
        $data = $request->validate([
            'device_id' => ['required', 'string', 'max:40', 'regex:/^[A-Za-z0-9][A-Za-z0-9_-]*$/'],
            'name' => ['required', 'string', 'max:32', 'regex:/^[a-z][a-z0-9_-]*$/'],
            'kind' => ['required', 'in:led,servo'],
        ]);
        $actuator = DB::transaction(function () use ($data) {
            Device::firstOrCreate(['device_id' => $data['device_id']]);
            Device::whereKey($data['device_id'])->lockForUpdate()->firstOrFail();
            $row = Actuator::firstOrCreate(['device_id' => $data['device_id'], 'name' => $data['name']],
                ['kind' => $data['kind']]);
            abort_if($row->kind !== $data['kind'], 409, 'Jenis aktuator sudah terdaftar dengan nilai berbeda.');
            return $row;
        });
        return response()->json($actuator->refresh(), $actuator->wasRecentlyCreated ? 201 : 200);
    }

    private function value(Request $request, Actuator $actuator): int
    {
        $value = $request->input('value');
        $max = $actuator->kind === 'led' ? 1 : 180;
        if (! is_int($value) || $value < 0 || $value > $max) {
            throw ValidationException::withMessages(['value' => "Gunakan bilangan bulat JSON dari 0 sampai {$max}."]);
        }
        return $value;
    }

    private function identity(Request $request): array
    {
        return $request->validate(['boot_id' => ['required', 'string', 'regex:/^[a-f0-9]{16}$/'],
            'sequence' => ['required', 'integer', 'between:1,2147483647']]);
    }

    private function expire(Actuator $actuator): void
    {
        ActuatorCommand::where('actuator_id', $actuator->id)->where('status', 'pending')
            ->where('expires_at', '<=', now())->update(['status' => 'expired']);
    }

    public function command(Request $request, Actuator $actuator): JsonResponse
    {
        $value = $this->value($request, $actuator);
        $command = DB::transaction(function () use ($actuator, $value) {
            $row = Actuator::whereKey($actuator->id)->lockForUpdate()->firstOrFail();
            $this->expire($row);
            ActuatorCommand::where('actuator_id', $row->id)->where('status', 'pending')
                ->update(['status' => 'superseded']);
            $row->update(['requested_value' => $value]);
            return ActuatorCommand::create(['actuator_id' => $row->id, 'value' => $value,
                'expires_at' => now()->addSeconds(30)]);
        });
        return response()->json($command->refresh(), 202);
    }

    public function pending(Actuator $actuator): JsonResponse
    {
        $command = DB::transaction(function () use ($actuator) {
            $row = Actuator::whereKey($actuator->id)->lockForUpdate()->firstOrFail();
            $this->expire($row);
            return ActuatorCommand::where('actuator_id', $row->id)->where('status', 'pending')->latest('id')->first();
        });
        return response()->json(['command' => $command]);
    }

    public function acknowledge(Request $request, Actuator $actuator): JsonResponse
    {
        $value = $this->value($request, $actuator);
        $data = $this->identity($request) + $request->validate(['command_id' => ['required', 'integer', 'min:1']]);
        $command = DB::transaction(function () use ($actuator, $value, $data) {
            $row = Actuator::whereKey($actuator->id)->lockForUpdate()->firstOrFail();
            $this->expire($row);
            $command = ActuatorCommand::where('actuator_id', $row->id)->findOrFail($data['command_id']);
            abort_if($command->value !== $value, 422, 'Nilai laporan tidak sesuai perintah.');
            abort_if($row->boot_id !== $data['boot_id'], 409, 'Laporkan boot perangkat terlebih dahulu.');
            // A retry must not roll back a newer state or add a second event.
            if ($command->status === 'applied') {
                return $command;
            }
            abort_if($command->status !== 'pending', 409, 'Perintah telah diganti atau kedaluwarsa.');
            abort_if($data['sequence'] <= $row->report_sequence, 409, 'Urutan laporan sudah dipakai.');
            $command->update(['status' => 'applied', 'acknowledged_at' => now()]);
            $row->update(['reported_value' => $value, 'reported_at' => now(), 'report_sequence' => $data['sequence']]);
            ActuatorStateEvent::create(['actuator_id' => $row->id, 'command_id' => $command->id,
                'value' => $value, 'reason' => 'command', 'boot_id' => $data['boot_id'], 'sequence' => $data['sequence']]);
            return $command;
        });
        return response()->json($command->refresh());
    }

    public function report(Request $request, Actuator $actuator): JsonResponse
    {
        $value = $this->value($request, $actuator);
        $data = $this->identity($request) + $request->validate(['reason' => ['required', 'in:boot,heartbeat']]);
        DB::transaction(function () use ($actuator, $value, $data) {
            $row = Actuator::whereKey($actuator->id)->lockForUpdate()->firstOrFail();
            if ($data['reason'] === 'boot' && $row->boot_id === $data['boot_id']) {
                return;
            }
            if ($data['reason'] === 'heartbeat') {
                abort_if($row->boot_id !== $data['boot_id'], 409, 'Laporkan boot perangkat terlebih dahulu.');
                abort_if($data['sequence'] <= $row->report_sequence, 409, 'Urutan laporan sudah dipakai.');
            } else {
                $this->expire($row);
                ActuatorCommand::where('actuator_id', $row->id)->where('status', 'pending')
                    ->update(['status' => 'superseded']);
            }
            if ($row->reported_value !== $value || $data['reason'] === 'boot') {
                ActuatorStateEvent::create(['actuator_id' => $row->id, 'value' => $value,
                    'reason' => $data['reason'], 'boot_id' => $data['boot_id'], 'sequence' => $data['sequence']]);
            }
            $row->update(['reported_value' => $value, 'boot_id' => $data['boot_id'],
                'report_sequence' => $data['sequence'], 'reported_at' => now()]);
        });
        return response()->json($actuator->refresh());
    }

    public function history(Request $request, Actuator $actuator): JsonResponse
    {
        $data = $request->validate(['limit' => ['nullable', 'integer', 'between:1,100']]);
        $limit = $data['limit'] ?? 20;
        return DB::transaction(function () use ($actuator, $limit) {
            $row = Actuator::whereKey($actuator->id)->lockForUpdate()->firstOrFail();
            $this->expire($row);
            return response()->json(['actuator' => $row,
                'commands' => ActuatorCommand::where('actuator_id', $row->id)->latest('id')->limit($limit)->get(),
                'events' => ActuatorStateEvent::where('actuator_id', $row->id)->latest('id')->limit($limit)->get()]);
        });
    }
}

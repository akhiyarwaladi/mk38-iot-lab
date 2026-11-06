<?php

namespace App\Http\Controllers;

use App\Models\Command;
use App\Models\Device;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class DeviceController extends Controller
{
    public function settings(Request $request, Device $device): JsonResponse
    {
        $data = $request->validate(['suhu_batas' => ['required', 'numeric', 'between:-40,80']]);
        $device->update($data);
        return response()->json($device->refresh());
    }

    public function store(Request $request, Device $device): JsonResponse
    {
        $data = $request->validate(['led' => ['required', 'boolean']]);
        $command = DB::transaction(function () use ($device, $data) {
            Device::whereKey($device->device_id)->lockForUpdate()->firstOrFail();
            Command::where('device_id', $device->device_id)->where('status', 'pending')
                ->update(['status' => 'superseded']);
            return Command::create(['device_id' => $device->device_id,
                'led' => $data['led'], 'expires_at' => now()->addSeconds(30)]);
        });
        return response()->json($command->refresh()->result(), 202);
    }

    public function pending(Device $device): JsonResponse
    {
        $command = Command::where('device_id', $device->device_id)->latest('id')->first();
        return response()->json(['command' => $command && $command->result()['status'] === 'pending'
            ? $command->result() : null]);
    }

    public function acknowledge(Request $request, Device $device): JsonResponse
    {
        $data = $request->validate(['command_id' => ['required', 'integer', 'min:1'],
            'led' => ['required', 'boolean']]);
        $command = DB::transaction(function () use ($device, $data) {
            $locked = Device::whereKey($device->device_id)->lockForUpdate()->firstOrFail();
            $command = Command::where('device_id', $device->device_id)->findOrFail($data['command_id']);
            abort_if($command->led !== (bool) $data['led'], 422, 'Status LED tidak sesuai perintah.');
            if ($command->status === 'applied') {
                return $command;
            }
            abort_if($command->result()['status'] !== 'pending', 409, 'Perintah telah diganti atau kedaluwarsa.');
            $command->update(['status' => 'applied', 'acknowledged_at' => now()]);
            $locked->update(['led' => $data['led'], 'reported_at' => now()]);
            return $command;
        });
        return response()->json($command->refresh()->result());
    }

    public function report(Request $request, Device $device): JsonResponse
    {
        $data = $request->validate(['led' => ['required', 'boolean']]);
        DB::transaction(function () use ($device, $data) {
            $locked = Device::whereKey($device->device_id)->lockForUpdate()->firstOrFail();
            $locked->update(['led' => $data['led'], 'reported_at' => now()]);
        });
        return response()->json($device->refresh());
    }
}

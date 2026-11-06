<?php

namespace App\Http\Controllers;

use App\Models\Command;
use App\Models\Device;
use App\Models\Sensor;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class DashboardController extends Controller
{
    private function filters(Request $request): array
    {
        return $request->validate([
            'device_id' => ['sometimes', 'required', 'string', 'regex:/^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$/'],
            'limit' => ['sometimes', 'integer', 'between:1,100'],
        ]);
    }

    public function data(Request $request): JsonResponse
    {
        $filters = $this->filters($request);
        $ids = Device::orderBy('device_id')->pluck('device_id');
        $id = $filters['device_id'] ?? $ids->first();
        $device = $id ? Device::find($id) : null;
        $rows = $id ? Sensor::where('device_id', $id)->latest('id')->limit($filters['limit'] ?? 50)->get() : collect();
        $latest = $rows->first();
        $age = $latest ? max(0, (int) $latest->created_at->diffInSeconds(now(), false)) : null;
        return response()->json([
            'server_time' => now()->toIso8601String(), 'devices' => $ids,
            'selected_device' => $id, 'device' => $device, 'latest' => $latest,
            'age_seconds' => $age, 'online' => $age !== null && $age <= 30,
            'warning' => $latest && $device && $latest->suhu >= $device->suhu_batas,
            'readings' => $rows->reverse()->values(),
            'commands' => $id ? Command::where('device_id', $id)->latest('id')->limit(5)->get()
                ->map(fn ($command) => $command->result()) : [],
        ])->header('Cache-Control', 'no-store');
    }

    public function csv(Request $request)
    {
        $filters = $this->filters($request);
        $bound = $request->validate(['until_id' => ['sometimes', 'integer', 'min:1']]);
        $query = Sensor::query()->latest('id');
        if (isset($filters['device_id'])) {
            $query->where('device_id', $filters['device_id']);
        }
        if (isset($bound['until_id'])) {
            $query->where('id', '<=', $bound['until_id']);
        }
        $rows = $query->limit($filters['limit'] ?? 50)->get()->reverse();
        return response()->streamDownload(function () use ($rows) {
            $output = fopen('php://output', 'w');
            fputcsv($output, ['id', 'device_id', 'suhu_celsius', 'kelembapan_persen', 'diterima_utc'], ',', '"', '');
            foreach ($rows as $row) {
                fputcsv($output, [$row->id, $row->device_id, $row->suhu, $row->kelembapan,
                    $row->created_at->toIso8601String()], ',', '"', '');
            }
            fclose($output);
        }, 'sensor.csv', ['Content-Type' => 'text/csv; charset=UTF-8']);
    }
}

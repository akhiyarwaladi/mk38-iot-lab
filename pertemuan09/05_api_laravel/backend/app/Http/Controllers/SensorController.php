<?php

namespace App\Http\Controllers;

use App\Http\Requests\StoreSensorRequest;
use App\Models\Sensor;
use App\Models\Device;
use Illuminate\Support\Facades\DB;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class SensorController extends Controller
{
    public function store(StoreSensorRequest $request): JsonResponse
    {
        $sensor = DB::transaction(function () use ($request) {
            Device::firstOrCreate(['device_id' => $request->validated('device_id')]);
            return Sensor::create($request->validated())->refresh();
        });

        return response()->json($sensor, 201)
            ->header('Location', '/api/v1/sensor/'.$sensor->id);
    }

    public function index(Request $request): JsonResponse
    {
        $pilihan = $request->validate([
            'device_id' => ['sometimes', 'required', 'string', 'regex:/^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$/'],
            'limit' => ['sometimes', 'integer', 'between:1,100'],
        ]);
        $query = Sensor::query()->orderByDesc('id');
        if (isset($pilihan['device_id'])) {
            $query->where('device_id', $pilihan['device_id']);
        }

        return response()->json($query->limit($pilihan['limit'] ?? 20)->get());
    }

    public function show(Sensor $sensor): JsonResponse
    {
        return response()->json($sensor);
    }
}


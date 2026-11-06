<?php

use App\Http\Controllers\SensorController;
use App\Http\Controllers\DeviceController;
use App\Http\Controllers\DashboardController;
use Illuminate\Support\Facades\Route;

Route::get('/v1/health', fn () => response()->json(['status' => 'ok']));
Route::post('/v1/sensor', [SensorController::class, 'store']);
Route::get('/v1/sensor', [SensorController::class, 'index']);
Route::get('/v1/sensor/{sensor}', [SensorController::class, 'show']);
Route::get('/v1/pemantauan', [DashboardController::class, 'data']);
Route::get('/v1/ekspor.csv', [DashboardController::class, 'csv']);
Route::put('/v1/perangkat/{device}/pengaturan', [DeviceController::class, 'settings']);
Route::post('/v1/perangkat/{device}/perintah', [DeviceController::class, 'store']);
Route::get('/v1/perangkat/{device}/perintah', [DeviceController::class, 'pending']);
Route::post('/v1/perangkat/{device}/konfirmasi', [DeviceController::class, 'acknowledge']);
Route::post('/v1/perangkat/{device}/status', [DeviceController::class, 'report']);


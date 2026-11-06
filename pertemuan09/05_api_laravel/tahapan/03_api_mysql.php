<?php

use App\Http\Controllers\SensorController;
use Illuminate\Support\Facades\Route;

Route::get('/v1/health', fn () => response()->json(['status' => 'ok']));
Route::post('/v1/sensor', [SensorController::class, 'store']);
Route::get('/v1/sensor', [SensorController::class, 'index']);
Route::get('/v1/sensor/{sensor}', [SensorController::class, 'show']);


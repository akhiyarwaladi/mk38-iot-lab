<?php

use App\Http\Controllers\ActuatorController;
use Illuminate\Support\Facades\Route;

Route::get('/aktuator', [ActuatorController::class, 'index']);
Route::post('/aktuator', [ActuatorController::class, 'register']);
Route::get('/aktuator/{actuator}/riwayat', [ActuatorController::class, 'history']);
Route::post('/aktuator/{actuator}/perintah', [ActuatorController::class, 'command']);
Route::get('/aktuator/{actuator}/perintah', [ActuatorController::class, 'pending']);
Route::post('/aktuator/{actuator}/konfirmasi', [ActuatorController::class, 'acknowledge']);
Route::post('/aktuator/{actuator}/status', [ActuatorController::class, 'report']);

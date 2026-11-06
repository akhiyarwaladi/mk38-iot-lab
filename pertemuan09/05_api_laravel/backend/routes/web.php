<?php

use Illuminate\Support\Facades\Route;
use App\Models\Sensor;

Route::view('/dashboard', 'dashboard');
Route::view('/latihan/nilai', 'latest');
Route::get('/latihan/tabel', fn () => view('table', ['rows' => Sensor::latest('id')->limit(10)->get()]));

Route::get('/', fn () => response()->json([
    'nama' => 'API Sensor MK38',
    'health' => '/api/v1/health',
    'sensor' => '/api/v1/sensor',
]));

<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/v1/health', fn () => response()->json(['status' => 'ok']));
Route::post('/v1/sensor', function (Request $request) {
    $data = $request->validate([
        'device_id' => ['required', 'string', 'regex:/^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$/'],
        'suhu' => ['required', 'numeric', 'between:-40,80'],
        'kelembapan' => ['required', 'numeric', 'between:0,100'],
    ]);

    return response()->json(['diterima' => $data, 'tersimpan' => false]);
});


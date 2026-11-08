Route::get('/latihan/tabel', fn () => view('table', [
    'rows' => Sensor::latest('id')->limit(10)->get(),
]));

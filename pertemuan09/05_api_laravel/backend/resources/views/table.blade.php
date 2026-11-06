<!doctype html>
<html lang="id">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tabel sensor sederhana | Praktikum MK38</title>
    <link rel="stylesheet" href="{{ asset('dashboard.css') }}">
</head>
<body>
<header class="site-header"><a class="brand" href="/dashboard">MK38 / Internet of Things</a><a href="/dashboard">Buka dashboard</a></header>
<main><div class="page-heading"><h1>Tabel sensor sederhana</h1><p>Latihan Blade: Laravel membaca MySQL lalu mengisi baris tabel saat halaman dibuka.</p></div>
    <section class="history"><div class="section-heading"><h2>Sepuluh kiriman terakhir</h2><a class="button secondary" href="/latihan/tabel">Baca ulang</a></div>
        <div class="table-wrap" tabindex="0" role="region" aria-label="Tabel kiriman sensor"><table><thead><tr><th>ID</th><th>Perangkat</th><th>Suhu (°C)</th><th>Kelembapan (%)</th></tr></thead><tbody>
        @forelse ($rows as $row)
            <tr><td>{{ $row->id }}</td><td>{{ $row->device_id }}</td><td>{{ $row->suhu }}</td><td>{{ $row->kelembapan }}</td></tr>
        @empty
            <tr><td colspan="4">Belum ada kiriman. Jalankan firmware sensor sebelum membaca ulang halaman.</td></tr>
        @endforelse
        </tbody></table></div>
    </section>
</main><footer>Halaman latihan mengikuti tampilan lembar praktikum terang. Data diperbarui ketika halaman dibuka ulang.</footer>
</body>
</html>

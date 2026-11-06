<!doctype html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Pemantauan ruangan | Praktikum MK38</title>
    <link rel="stylesheet" href="{{ asset('dashboard.css') }}">
    <script src="{{ asset('dashboard.js') }}" defer></script>
</head>
<body>
<a class="skip-link" href="#utama">Lewati ke pemantauan</a>
<header class="site-header">
    <a href="/dashboard" class="brand">MK38 / Internet of Things</a>
    <div class="header-actions"><a href="/api/v1/health">Periksa API</a>
        <label class="check"><input type="checkbox" id="dark-mode"> Tema gelap</label></div>
</header>
<main id="utama">
    <div class="page-heading"><h1>Pemantauan ruangan</h1>
        <p>Pilih perangkat, amati kiriman sensor, lalu periksa hasil kendali LED.</p></div>
    <form id="filter-form" class="filter-form">
        <div class="field"><label for="device">Perangkat</label><select id="device"><option value="">Memuat perangkat…</option></select></div>
        <div class="field"><label for="limit">Riwayat yang ditampilkan</label><select id="limit"><option value="20">20 kiriman</option><option value="50" selected>50 kiriman</option><option value="100">100 kiriman</option></select></div>
        <button type="submit" id="refresh">Perbarui data</button>
        <label class="check"><input type="checkbox" id="auto-refresh" checked> Otomatis setiap 5 detik</label>
    </form>
    <p id="network" class="notice" role="status">Memuat kiriman dari API…</p>
    <p id="feedback" class="feedback" role="status" aria-live="polite"></p>
    <div class="workspace">
        <section class="readings" aria-labelledby="readings-title">
            <div class="section-heading"><h2 id="readings-title">Pembacaan terbaru</h2><span id="connection">Menunggu data</span></div>
            <p id="last-seen" class="muted">Waktu penerimaan akan tampil setelah data dimuat.</p>
            <dl class="measurements"><div><dt>Suhu</dt><dd id="temperature" class="missing">Memuat</dd></div><div><dt>Kelembapan</dt><dd id="humidity" class="missing">Memuat</dd></div></dl>
            <p id="temperature-note" class="condition">Ambang suhu adalah aturan latihan, bukan batas keselamatan.</p>
            <div class="chart-block"><h3>Perubahan suhu <span>°C</span></h3><svg id="chart-temperature" role="img" aria-label="Grafik suhu belum tersedia"></svg></div>
            <div class="chart-block"><h3>Perubahan kelembapan <span>% RH</span></h3><svg id="chart-humidity" role="img" aria-label="Grafik kelembapan belum tersedia"></svg></div>
            <p id="chart-note" class="muted">Grafik memakai waktu penerimaan server. Data belum dimuat.</p>
        </section>
        <aside class="control" aria-labelledby="control-title">
            <h2 id="control-title">Kendali LED</h2>
            <p>LED contoh berada pada GPIO 23. Status berubah setelah perangkat melaporkan hasilnya.</p>
            <dl class="control-state"><dt>Terakhir dilaporkan ESP32</dt><dd id="reported-led">Belum ada laporan</dd></dl>
            <p id="reported-at" class="muted">Jalankan firmware kendali untuk menerima laporan LED.</p>
            <div class="button-row"><button type="button" id="led-on" disabled>Nyalakan LED</button><button type="button" id="led-off" class="secondary" disabled>Matikan LED</button></div>
            <p class="muted">Perintah berlaku 30 detik. Jika ESP32 tidak mengambilnya, perintah akan kedaluwarsa.</p>
            <form id="settings-form" class="settings-form">
                <label for="threshold">Ambang peringatan suhu (°C)</label>
                <div class="setting-row"><input id="threshold" type="number" min="-40" max="80" step="0.1" required disabled><button type="submit" id="save-threshold" class="secondary" disabled>Simpan ambang</button></div>
                <p class="muted">Nilai ini hanya mengubah indikator dashboard; LED tetap dikendalikan melalui tombol.</p>
            </form>
            <h3>Riwayat perintah</h3>
            <ol id="commands" class="commands"><li>Belum ada data perintah.</li></ol>
        </aside>
    </div>
    <section class="history" aria-labelledby="history-title">
        <div class="section-heading"><div><h2 id="history-title">Bukti kiriman</h2><p id="history-note" class="muted">Catatan yang sama dapat diperiksa di MySQL.</p></div><a id="csv" class="button secondary" href="/api/v1/ekspor.csv?limit=50">Unduh CSV</a></div>
        <div class="table-wrap" tabindex="0" role="region" aria-label="Tabel riwayat sensor, dapat digeser jika layar sempit"><table><thead><tr><th scope="col">ID</th><th scope="col">Diterima (WIB)</th><th scope="col">Suhu (°C)</th><th scope="col">Kelembapan (%)</th></tr></thead><tbody id="history"><tr><td colspan="4">Memuat riwayat…</td></tr></tbody></table></div>
    </section>
    <noscript><p class="notice">Dashboard memerlukan JavaScript untuk memperbarui data. Anda tetap dapat <a href="/api/v1/ekspor.csv">mengunduh CSV</a> dari API.</p></noscript>
</main>
<footer><a href="/latihan/tabel">Mulai dari tabel sederhana</a><p>Praktikum MK38 · Satu perangkat contoh. Konfirmasi menunjukkan laporan firmware, bukan pengukuran arus pada LED.</p></footer>
</body>
</html>

<!doctype html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Satu pembacaan dari API | Praktikum MK38</title>
    <link rel="stylesheet" href="{{ asset('dashboard.css') }}">
</head>
<body>
<header class="site-header"><a class="brand" href="/dashboard">MK38 / Internet of Things</a><a href="/latihan/tabel">Lihat tabel Blade</a></header>
<main>
    <div class="page-heading"><h1>Satu pembacaan dari API</h1><p>Latihan JavaScript: minta satu catatan JSON, lalu isi teks pada halaman.</p></div>
    <section class="history" aria-labelledby="judul-nilai">
        <h2 id="judul-nilai">Pilih perangkat yang sudah mengirim data</h2>
        <form id="baca-form" class="filter-form">
            <div class="field"><label for="device-id">ID perangkat</label><input type="text" id="device-id" value="esp32-kelompok-01" maxlength="40" pattern="[A-Za-z0-9][A-Za-z0-9_-]{0,39}" required></div>
            <button id="baca" type="submit">Baca satu catatan</button>
        </form>
        <p id="hasil" role="status">Isi ID yang sama dengan firmware, lalu pilih Baca satu catatan.</p>
        <p id="nilai">Suhu dan kelembapan belum diminta.</p>
        <p><a href="/dashboard">Lanjutkan ke grafik dan kendali</a></p>
    </section>
</main>
<footer>Halaman ini membaca ulang data hanya ketika formulir dikirim. Kiriman baru berasal dari ESP32.</footer>
<script>
const form = document.getElementById('baca-form');
const button = document.getElementById('baca');
const hasil = document.getElementById('hasil');
const nilai = document.getElementById('nilai');
form.addEventListener('submit', async event => {
    event.preventDefault();
    button.disabled = true;
    hasil.textContent = 'Meminta satu catatan dari API…';
    nilai.textContent = 'Menunggu respons.';
    const id = document.getElementById('device-id').value;
    try {
        const url = '/api/v1/sensor?limit=1&device_id=' + encodeURIComponent(id);
        const response = await fetch(url, {cache:'no-store', signal:AbortSignal.timeout(8000), headers:{Accept:'application/json'}});
        const rows = await response.json();
        if (!response.ok) throw new Error(rows.message || 'HTTP ' + response.status);
        if (!rows.length) {
            hasil.textContent = 'Belum ada kiriman untuk ID ini. Jalankan ESP32 atau periksa ID perangkat.';
            nilai.textContent = 'Belum ada nilai sensor.';
            return;
        }
        hasil.textContent = 'Catatan #' + rows[0].id + ' dari ' + rows[0].device_id;
        nilai.textContent = 'Suhu ' + rows[0].suhu + ' °C; kelembapan ' + rows[0].kelembapan + '%.';
    } catch (error) {
        hasil.textContent = 'Pembacaan gagal: ' + error.message + '. Periksa Laravel dan MySQL, lalu coba lagi.';
        nilai.textContent = 'Nilai belum dapat dibaca.';
    } finally {
        button.disabled = false;
    }
});
</script>
</body>
</html>

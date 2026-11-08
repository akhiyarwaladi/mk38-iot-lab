<!doctype html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Aktuator | Praktikum MK38</title>
    <link rel="stylesheet" href="/dashboard.css">
    <link rel="stylesheet" href="/actuators.css">
    <script src="/actuators.js" defer></script>
</head>
<body>
<a href="#main" class="skip-link">Langsung ke praktik</a>
<header class="site-header">
    <a class="brand" href="/dashboard">MK38 · Praktikum IoT</a>
    <div class="header-actions"><a href="/latihan/tabel">Tabel sensor</a><button type="button" class="secondary" id="theme">Tema gelap</button></div>
</header>
<main id="main">
    <div class="page-heading"><h1>Perintah dan status aktuator</h1>
        <p>Bandingkan target operator dengan laporan firmware, lalu periksa riwayatnya di MySQL.</p></div>
    <form id="selection" class="filter-form">
        <div class="field"><label for="actuator">Perangkat / aktuator</label><select id="actuator" disabled><option>Memuat daftar…</option></select></div>
        <button type="submit" class="secondary" id="refresh">Perbarui data</button>
        <label class="check"><input type="checkbox" id="automatic" checked>Perbarui setiap 2 detik</label>
    </form>
    <p id="connection" class="notice" role="status">Menghubungkan ke API lokal…</p>
    <div class="workspace actuator-workspace">
        <section class="readings" aria-labelledby="state-title">
            <h2 id="state-title">Nilai yang tersimpan</h2>
            <dl class="measurements"><div><dt>Diminta operator</dt><dd id="requested">Belum ada</dd></div><div><dt>Dilaporkan firmware</dt><dd id="reported">Belum ada</dd></div></dl>
            <p id="freshness" class="condition">Belum menerima laporan firmware.</p>
            <dl class="actuator-meta"><dt>ID aktuator</dt><dd id="actuator-id">Belum dipilih</dd><dt>Boot perangkat</dt><dd id="boot-id">Belum ada</dd><dt>Laporan terakhir (WIB)</dt><dd id="reported-at">Belum ada</dd></dl>
            <p class="muted">LED: 0 = mati, 1 = menyala. Servo: sudut 0 sampai 180°. Laporan servo menunjukkan nilai PWM yang ditetapkan firmware, tanpa sensor posisi mekanis.</p>
        </section>
        <section class="control" aria-labelledby="command-title">
            <h2 id="command-title">Kirim perintah</h2>
            <p>Perintah berlaku 30 detik. Status belum dianggap diterapkan sebelum ESP32 mengirim konfirmasi.</p>
            <div id="led-controls" class="button-row" hidden><button type="button" data-value="1" disabled>Nyalakan LED</button><button type="button" class="secondary" data-value="0" disabled>Matikan LED</button></div>
            <form id="servo-controls" hidden><label for="angle">Sudut servo (°)</label><div class="setting-row"><input type="number" id="angle" min="0" max="180" step="1" value="90" required disabled><button type="submit" disabled>Kirim sudut</button></div></form>
            <p id="feedback" class="feedback" role="status">Pilih aktuator setelah firmware mendaftarkannya.</p>
            <p class="muted">Saat ESP32 memulai ulang, output kembali ke nilai awal 0. Target terakhir tetap tersimpan sebagai catatan; kirim perintah baru untuk menjalankannya kembali.</p>
        </section>
    </div>
    <section class="history" aria-labelledby="commands-title"><h2 id="commands-title">Riwayat perintah</h2><p class="muted">pending = menunggu, applied = dikonfirmasi, superseded = diganti, expired = kedaluwarsa.</p>
        <div class="table-wrap" tabindex="0" role="region" aria-label="Riwayat perintah aktuator"><table><thead><tr><th scope="col">ID</th><th scope="col">Target</th><th scope="col">Status</th><th scope="col">Konfirmasi (WIB)</th></tr></thead><tbody id="command-rows"><tr><td colspan="4">Belum ada perintah.</td></tr></tbody></table></div></section>
    <section class="history" aria-labelledby="events-title"><h2 id="events-title">Riwayat status firmware</h2><p class="muted">Dicatat saat boot, penerapan perintah, atau nilai laporan berubah. Heartbeat dengan nilai sama hanya memperbarui waktu terakhir.</p>
        <div class="table-wrap" tabindex="0" role="region" aria-label="Riwayat status firmware"><table><thead><tr><th scope="col">ID</th><th scope="col">Nilai</th><th scope="col">Sumber</th><th scope="col">ID perintah</th><th scope="col">Diterima (WIB)</th></tr></thead><tbody id="event-rows"><tr><td colspan="5">Belum ada laporan.</td></tr></tbody></table></div></section>
    <noscript><p class="notice error">Aktifkan JavaScript untuk mengirim perintah. JSON tetap dapat dibaca pada <a href="/api/v1/aktuator">daftar aktuator</a>.</p></noscript>
</main>
<footer><p>Laboratorium lokal tanpa autentikasi. Jalankan server pada 127.0.0.1. Penggunaan di jaringan bersama memerlukan autentikasi dan HTTPS.</p></footer>
</body>
</html>

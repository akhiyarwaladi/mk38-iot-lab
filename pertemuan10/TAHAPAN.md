# Urutan latihan pertemuan 10

ESP32: 01_publish → 02_sensor → 03_kendali. Node-RED: tahap 1 → 2 → 3 → 4. Ekspor perubahan editor sebelum mengganti tahap.

Baca bagian pengembangan kode bertahap pada PDF pertemuan ini sebelum menjalankan kode lengkap.

## Prasyarat dan berkas pembuka

Setup/loop, Wi-Fi, DHT22, JSON; dependensi Node-RED; satu topic root pada semua client.

## Titik awal yang kecil

01_publish mengirim teks; node tahapan/jalankan.js 1 hanya memuat MQTT in dan Debug beserta config.

## Perubahan antarversi

Teks MQTT, JSON sensor, callback LED; flow mentah, parsing/validasi, SQLite, lalu dashboard/kendali/riwayat.

## Cara menjalankan

Buka satu proyek ESP32 per tahap; di node_red jalankan node tahapan/jalankan.js 1, 2, 3, atau 4, bergantian setelah Ctrl+C.

## Bukti sebelum lanjut

Subscriber menerima teks; input salah ditolak; data valid menambah SQLite; GPIO dikonfirmasi kembali.

## Hubungan ke versi lengkap dan batas

Instruksi membedakan validasi_awal.js dari validasi.js yang menunggu dbSiap. Flow lengkap menjadi gabungan cabang yang telah diperiksa.

Simpan hasil setiap tahap. Perintah harus dijalankan dari folder yang disebut, bukan dari folder ZIP yang belum diekstrak. Pada proyek ESP32, versi CPP disimpan di luar src; satu main.cpp aktif pada setiap build. Simpan perubahan sendiri sebelum menyalin versi lain. Hentikan proses/simulasi versi sebelumnya sebelum mengganti tahap.

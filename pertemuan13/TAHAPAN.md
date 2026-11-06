# Urutan latihan pertemuan 13

01_teks.cpp → 02_sensor.cpp → 99_lengkap.cpp; sesudah itu uji CA/password/hak akses dengan prosedur modul.

Baca bagian pengembangan kode bertahap pada PDF pertemuan ini sebelum menjalankan kode lengkap.

## Prasyarat dan berkas pembuka

MQTT biasa pertemuan 10; CA/NTP/hostname dari HTTPS; config dan topic root; satu versi aktif di src.

## Titik awal yang kecil

esp32_tls/versi/01_teks.cpp mengirim Halo melalui TLS, tanpa DHT22 atau callback LED.

## Perubahan antarversi

WiFiClientSecure + CA/waktu, pesan teks, JSON DHT22, callback/subscribe LED, lalu konfirmasi retained.

## Cara menjalankan

Copy-Item versi/01_teks.cpp atau 02_sensor.cpp ke src/main.cpp, pio run; samakan konfigurasi subscriber TLS.

## Bukti sebelum lanjut

Subscriber menerima teks; JSON berubah sesuai sensor; on/off/salah diuji pada versi lengkap. Field led=false tahap sensor diberi batas jelas.

## Hubungan ke versi lengkap dan batas

99_lengkap.cpp menggabungkan ketiga tahap. Broker publik, broker lokal autentikasi, dan akun privat dijelaskan sebagai lingkungan yang berbeda.

Simpan hasil setiap tahap. Perintah harus dijalankan dari folder yang disebut, bukan dari folder ZIP yang belum diekstrak. Pada proyek ESP32, versi CPP disimpan di luar src; satu main.cpp aktif pada setiap build. Simpan perubahan sendiri sebelum menyalin versi lain. Hentikan proses/simulasi versi sebelumnya sebelum mengganti tahap.

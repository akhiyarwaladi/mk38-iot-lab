# Backend Laravel untuk API sensor MK38

Mulai dari [panduan lab](../README.md), lalu ikuti versi route di `../tahapan/`. Proyek memakai Laravel 12, PHP 8.2+, dan MySQL. Versi dependency terkunci pada `composer.lock`. Jalankan perintah Artisan dari folder ini.

Konfigurasi pribadi disimpan pada `.env`. Contoh tersedia pada `.env.example`; sesuaikan port dan password dengan server MySQL. API lokal dijalankan dengan `php artisan serve --host=127.0.0.1 --port=8000` setelah migration selesai.

`php artisan test --no-ansi` menjalankan uji sensor dan dashboard memakai database **terpisah** bernama `mk38_sensor_test`. Salin `.env` menjadi `.env.testing`, ubah `APP_ENV=testing` serta `DB_DATABASE=mk38_sensor_test`, dan siapkan database itu dengan hak akses pengguna lab. Uji akan membuat ulang tabel di database test; guard menolak nama database yang berbeda. Jangan memakai database berisi data yang perlu dipertahankan.

Sebelum menguji seluruh aplikasi, pastikan `routes/api.php` sudah memakai salinan `../tahapan/04_api_dashboard.php`; route pengantar 01 sampai 03 sengaja belum menyediakan endpoint dashboard.

Untuk membaca database praktik secara langsung, jalankan `php tests/inspect_database.php`. Perintah ini hanya membaca versi server, jumlah catatan, dan contoh data. Hasil uji tersimpan pada folder `../bukti`.

Setelah mengikuti tahap dasar, jalankan migration kedua dan aktifkan `../tahapan/04_api_dashboard.php` sesuai [panduan lanjut](../DASHBOARD_BERTAHAP.md). `/latihan/tabel` memperkenalkan Blade; `/dashboard` menampilkan grafik serta kendali. Tabel `devices` menyimpan pengaturan/laporan dan `commands` menyimpan perintah beserta konfirmasi. Firmware kendali lengkap tersedia pada `../esp32/versi/04_kendali.cpp`.

Kerangka Laravel bersumber dari [laravel/laravel](https://github.com/laravel/laravel) dan memakai [lisensi MIT](https://opensource.org/licenses/MIT).

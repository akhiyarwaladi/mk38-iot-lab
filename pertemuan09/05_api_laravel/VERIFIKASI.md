# Hasil uji lab API Laravel dan MySQL

Dokumen ini mencatat uji awal lab sensor, sebelum dashboard dan kendali ditambahkan. Hasil edisi terbaru ada pada [verifikasi dashboard](VERIFIKASI_DASHBOARD.md). Angka 77 kiriman, enam uji, serta tiga versi firmware di bawah adalah catatan uji awal, bukan ringkasan paket terbaru.

Diperiksa pada 6 November 2026. Lingkungan: Windows, PHP 8.2.12, Laravel 12.71.0, Composer 2.11.1, dan MySQL Community Server 8.4.13. Aplikasi berjalan pada `127.0.0.1:8000`; MySQL pengujian memakai port 3309. Konfigurasi contoh untuk mahasiswa memakai port 3306 dan harus disesuaikan dengan server masing-masing.

## Hasil yang dibuktikan

| Pemeriksaan | Hasil dan bukti |
|---|---|
| Pembuatan tabel dari nol | Migration `create_sensors_table` berhasil pada database MySQL baru. |
| Route, input, database, daftar, dan ID | Enam uji Laravel lulus; jumlah assertion dan perintah tercatat pada `bukti/laravel_tests.json`. Pengujian memakai MySQL `mk38_sensor_test`, terpisah dari data simulator. |
| Versi API bertahap | Route health diuji sebelum route POST; tahap penerimaan JSON mengembalikan `tersimpan: false` tanpa menulis baris. |
| Ketiga versi firmware | Build PlatformIO lulus untuk `01_health.cpp`, `02_kirim_contoh.cpp`, dan `03_sensor.cpp`; lihat `bukti/firmware_builds.json`. |
| ESP32 ke Laravel | Firmware sensor dijalankan di Wokwi VS Code. Serial menampilkan status 201 dan ID dari Laravel; dua screenshot asli tersedia pada `bukti/`. |
| Isi MySQL cocok dengan pembacaan API | Tercatat 77 kiriman ESP32. Contoh ID 1 = 28/65, ID 49 = 32/70, dan ID 66 = 35/75. Script memeriksa nilai tersebut melalui GET dan query MySQL terpisah; lihat `bukti/live_result.json`. |
| Data setelah server API dimulai ulang | Proses PHP API dihentikan lalu dijalankan kembali. ID 1 beserta nilai dan waktu yang sama tetap dapat dibaca. |

Saat dua slider DHT22 diubah berurutan, pasangan sementara 32/65 juga tersimpan. Catatan itu dipertahankan dalam bukti; dua perubahan masukan tidak terjadi serentak. Waktu pada respons API adalah waktu server UTC. Screenshot memakai tampilan lokal komputer, sehingga jam pada keduanya dapat berbeda zona waktu.

## Batas pengujian

Firmware lengkap sensor sudah dioperasikan pada simulator. Dua versi pengantar firmware diuji kompilasinya; keduanya belum dijalankan terpisah di simulator. Keenam uji Laravel memakai database MySQL nyata, bukan SQLite atau database tiruan. Uji pemahaman mahasiswa belum dilakukan.

API masih berupa lab lokal HTTP tanpa autentikasi perangkat. Penerapan pada server internet, HTTPS, API key/Sanctum, akses beberapa kelompok, dan ESP32 fisik belum diuji. Firmware belum mengantrekan data saat API mati dan belum mencegah duplikasi kiriman. Hal itu menjadi pengembangan setelah alur dasar dipahami.

Sumber proyek baru berada pada folder `api_sensor`, sebagai lab pendamping. PDF seri pertemuan 9 sampai 15 dan paket mingguannya belum diganti oleh lab ini. Kode, panduan langkah, serta bukti lab disertakan dalam paket terpisah `api_sensor_laravel_mysql.zip`.

## Tinjauan penulisan dan urutan belajar

- PASS: persiapan PHP/Composer/MySQL diletakkan sebelum kelas; istilah dan file dijelaskan ketika dipakai.
- PASS: satu route health mendahului POST; penerimaan dipisahkan dari penyimpanan; kiriman tetap mendahului data DHT22.
- PASS: tiap tahap menyebut folder terminal, berkas yang diganti, perintah, hasil, dan pemeriksaan sebelum lanjut.
- PASS: hostname laptop dan ESP32 dibedakan; middleware API didaftarkan secara eksplisit; panduan tidak mematikan CSRF global.
- PASS: bukti keberhasilan meliputi respons 201, GET ID, dan SELECT MySQL; status Wi-Fi tidak dipakai sebagai bukti penyimpanan.
- PASS: narasi menyebut keterbatasan yang benar-benar ada, tanpa menjanjikan semua kondisi jaringan atau pemahaman mahasiswa sudah diuji.

Penyuntingan mengacu pada `no-ai-slop` dan `bahasa-inti`: mempertahankan nama aplikasi/identifier, memakai kalimat instruksi langsung, serta menghindari slogan dan padanan teknis yang tidak lazim. Tidak dibuat desain antarmuka baru; halaman awal backend hanya mengembalikan JSON.

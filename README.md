# Praktikum Internet of Things, MK38

Kode untuk pertemuan 9 sampai 15, Program Studi Informatika Universitas Jambi.

| Pertemuan | Isi |
|---|---|
| [9](pertemuan09) | Wi-Fi, REST, Laravel, MySQL, dashboard, dan kendali ESP32 |
| [10](pertemuan10) | MQTT, Node-RED, SQLite |
| [11](pertemuan11) | Cloud, REST/MQTT, proyek |
| [12](pertemuan12) | Rangkaian dan enclosure |
| [13](pertemuan13) | TLS, autentikasi, kendali lokal |
| [14](pertemuan14) | Gateway dan metrik |
| [15](pertemuan15) | Pengujian dan pengumpulan proyek |

Mulai API dan dashboard dari [panduan Laravel](pertemuan09/05_api_laravel/README.md). Instal dependency menurut lockfile dan isi konfigurasi lokal dari contoh.

Berkas dalam folder proyek adalah program atau konfigurasi yang dipakai tutorial. Folder `cuplikan` menyimpan kotak perintah, contoh respons, atau potongan penjelasan; cuplikan tidak selalu merupakan program utuh. Gunakan konteks folder dan langkah pada modul sebelum menjalankannya.

## Di mana menaruh C++?

Sunting kode di VS Code. PlatformIO mengompilasinya; Wokwi menjalankan firmware hasil build. Buka folder yang langsung memuat `platformio.ini`. Program aktif latihan berada di `src/main.cpp`, header lokal di `include/`, serta `wokwi.toml` dan `diagram.json` di root proyek.

Setiap file di `versi/` adalah versi program utuh. Salin satu versi ke `src/main.cpp`, simpan, Build, lalu mulai ulang Wokwi. Jangan menaruh semua versi ke `src/` karena definisi `setup()`/`loop()` akan rangkap. Kotak cuplikan menjelaskan bagian program; jangan mengganti seluruh berkas dengan cuplikan.

Angka 01/02/03 adalah penanda proyek/tahap dalam paket. Pertahankan nama folder saat mengikuti tutorial agar jalur perintah cocok. Pada lab Laravel, buka `05_api_laravel/esp32` untuk PlatformIO; jalankan PHP/Composer dari `05_api_laravel/backend`. PHP, SQL, perintah PowerShell, dan contoh respons tidak ditempel ke `main.cpp`. Petunjuk di atas setiap kotak pada PDF menyebut alat, folder, dan berkas tujuannya.

Kredensial contoh memakai placeholder. Jangan unggah `.env`, `secrets.h`, password, private key, atau database pribadi. Salinan ini diekspor dari sumber modul; manifest mencatat asal berkas serta SHA-256. Laravel dan dependency mempertahankan lisensi asalnya.

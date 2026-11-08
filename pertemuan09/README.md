# Praktik pertemuan 9: Wi-Fi, Laravel, MySQL, dan dashboard

Buka satu proyek pada satu waktu. Urutan jalur utama mengikuti PDF:

1. `01_wifi`: ESP32 bergabung ke Wokwi-GUEST dan menampilkan IP.
2. `02_sensor`: baca DHT22 setiap dua detik; ubah nilainya di simulator.
3. [`05_api_laravel`](05_api_laravel/README.md): buat API health, terima JSON,
   simpan MySQL, kirim ESP32, lalu tampilkan tabel, satu nilai JSON, dan
   dashboard dengan grafik/CSV serta konfirmasi kendali LED.

Nomor folder lama dipertahankan. `03_cloud` menjadi pengayaan ThingSpeak;
`04_server` dipakai untuk membandingkan layanan HTTP pada ESP32.

Firmware jalur sensor memakai rangkaian DHT22 dan LED yang sama. Pengayaan
aktuator memakai proyek terpisah dengan LED dan servo; ikuti
panduan `05_api_laravel/AKTUATOR_BERTAHAP.md`. Untuk Laravel, jalankan PHP
dari `05_api_laravel/backend` dan buka `05_api_laravel/esp32` sebagai
workspace PlatformIO. Siapkan PHP, Composer, MySQL, Python 3.10 atau lebih baru, dan dependency
sebelum kelas. Setiap proyek berdiri sendiri; server ESP32 tidak mengirim
ke ThingSpeak.

## Persiapan

Kode C++ disunting di **VS Code**, dikompilasi oleh **PlatformIO**, lalu
hasil build dijalankan oleh **Wokwi**. Buka satu folder yang langsung
berisi `platformio.ini`. Program aktif berada pada `src/main.cpp`; header
lokal pada `include/`. Folder `.pio` dibuat otomatis saat build.

Folder `01_wifi`, `02_sensor`, `03_cloud`, dan `04_server` adalah proyek
terpisah. Pertahankan namanya saat mengikuti modul agar perintah cocok;
angkanya bukan syarat PlatformIO. Folder `versi/` di dalam satu proyek
menyimpan program alternatif yang utuh. Salin **satu** versi ke
`src/main.cpp`, simpan, build, lalu mulai ulang Wokwi. Jangan menaruh semua
versi ke `src` sebagai `main2.cpp` atau `coba.cpp`, karena setiap versi
mendefinisikan `setup()` dan `loop()` sendiri.

Kotak berlabel **cuplikan** hanya membahas bagian program. Baca bagian itu
pada berkas utuh; jangan mengganti seluruh `main.cpp` dengan cuplikan.
Perintah penyalinan PowerShell khusus Windows; pada sistem lain gunakan
Explorer VS Code untuk menyalin berkas ke tujuan yang sama.
Uji HTTP memakai skrip Python yang dijalankan dari folder yang disebutkan.
SQL dijalankan pada klien MySQL. PHP/Blade/JavaScript dashboard berada
pada backend Laravel di laptop.

Pada `05_api_laravel`, workspace PlatformIO adalah subfolder `esp32`.
Terminal server Laravel dijalankan dari subfolder `backend`.

Pasang ekstensi `platformio.platformio-ide` dan `Wokwi.wokwi-vscode`.
PlatformIO menyertakan compiler dan manajer pustaka; Wokwi menjalankan
simulasi firmware. Jalankan `Wokwi: Request a new License` dari F1 untuk
aktivasi akun/lisensi. Periksa ketentuan akses yang ditampilkan Wokwi.
Panduan: https://docs.wokwi.com/vscode/getting-started

Buka folder tahap, tunggu PlatformIO siap, lalu pilih `PlatformIO: Build`.
Sesudah build berhasil, jalankan `Wokwi: Start Simulator` dari F1. Jalankan
ulang Build dan mulai ulang simulator setiap kali program berubah. Gunakan
Serial Monitor pada panel Wokwi untuk simulasi, bukan monitor port COM.

Terminal PlatformIO juga dapat dipakai:

```powershell
pio run
```

## Rangkaian

- DHT22 VCC ke 3V3; GND ke GND; SDA/data ke GPIO 15.
- Resistor pull-up 10 kiloohm dari SDA ke 3V3.
- GPIO 23 ke resistor 220 ohm, lalu anoda LED; katoda LED ke GND.
- Pin NC DHT22 dibiarkan tidak terhubung. Label SDA di sini adalah data
  DHT22, bukan bus I2C.

`diagram.json` sudah berisi seluruh sambungan.

## Tahap cloud

Buat channel ThingSpeak dengan Field 1 = Suhu dan Field 2 = Kelembapan.
Salin `include/secrets.example.h` menjadi `include/secrets.h`; isi Write API
Key milik channel tersebut. Berkas lokal itu diabaikan Git. Jangan sertakan
key pada laporan atau tangkapan layar.

Program mengirim JSON melalui HTTPS setiap sedikitnya 20 detik. Keberhasilan
memerlukan status HTTP 200 dan entry ID positif, lalu data terlihat pada
Private View. `root_ca.h` berisi sertifikat akar publik DigiCert Global Root
G2; NTP menyiapkan waktu untuk validasi TLS. Sertifikat rantai ThingSpeak
diperiksa pada 29 Oktober 2026. Jika rantainya berubah, perbarui CA dari
sumber resminya setelah memeriksa issuer; jangan menonaktifkan validasi TLS.

Write API Key channel demonstrasi dosen disertakan pada `03_cloud/include/secrets.demo.h` sesuai permintaan pengguna. Salin menjadi `secrets.h` untuk demonstrasi. Untuk kelompok, gunakan channel dan Write API Key sendiri. Build tanpa konfigurasi tetap berhasil, tetapi program meminta pengisian sebelum mengirim data.

## Tahap server

Selama simulator tahap 4 berjalan, buka http://localhost:8180.
`wokwi.toml` meneruskan port localhost 8180 ke port 80 ESP32 simulasi.
Jangan langsung membuka IP virtual yang dicetak ESP32.

Di terminal dari folder `04_server`, jalankan:

```text
python uji_http.py
```

Gunakan `python3` pada Linux/macOS atau `py -3` pada Windows jika itu nama
Python 3 yang tersedia. Pustaka standar sudah cukup; tidak perlu pip install.
Skrip membaca `/sensor`, kemudian mengirim form `state` ke `/led`.
Jalankan dengan `NILAI_LED = "on"`, cocokkan LED virtual, lalu ubah nilai
menjadi `"off"`, simpan, dan jalankan ulang.

`GET /sensor` mengembalikan JSON; `POST /led` mengubah LED lalu membalas
303 (browser diarahkan ke halaman utama; klien biasanya mengikuti menjadi
200). Ubah `NILAI_LED` menjadi `"salah"`, simpan, lalu jalankan ulang:
skrip menampilkan HTTP 400 dan LED tidak berubah. Pulihkan menjadi `"off"`.
Saat sensor
belum siap, respons sensor 503. Rute yang tidak tersedia membalas 404.

Server HTTP lokal ini untuk latihan. Ia belum memiliki autentikasi; gunakan
penerusan localhost saja. Pengamanan komunikasi dibahas pada pertemuan 13.

## Jika Wokwi VS Code belum dapat diaktifkan

Tahap 1 sampai 3 dapat dicoba di Wokwi web: buat proyek ESP32, salin
`src/main.cpp` ke `sketch.ino`, `diagram.json` ke tab diagram, dan header
dari `include/` bila ada. Tambahkan pustaka `DHT sensor library for ESPx`
di Library Manager. Gunakan key channel praktikum yang dapat diganti;
jangan membagikan proyek yang memuat key. Gateway publik Wokwi web tidak
menerima koneksi masuk; kendali browser tahap 4 memerlukan gateway yang
mendukung koneksi masuk atau ESP32 fisik. Keterbatasan ini tidak dapat
diselesaikan hanya dengan mengganti IP di browser.

Untuk ESP32 fisik, ubah SSID/password menjadi Wi-Fi 2,4 GHz, unggah program
melalui USB, lalu buka IP dari Serial Monitor dengan perangkat di LAN yang
sama. `localhost:8180` hanya untuk simulasi dengan konfigurasi yang diberikan.

## Channel demonstrasi

Channel demonstrasi dosen memiliki ID 3560582. Konfigurasi Write API Key tersedia pada `03_cloud/include/secrets.demo.h`, sesuai permintaan pengguna. Dari terminal PlatformIO di folder `03_cloud`, salin `include/secrets.demo.h` menjadi `include/secrets.h`, lalu build. Jalankan satu pengirim pada channel demonstrasi; kelompok menggunakan channel masing-masing. Read API Key tidak disertakan.

Bukti penulisan dari ESP32 virtual, pembacaan ulang ThingSpeak, serta kendali tersimpan pada folder bukti di ZIP sumber. Lihat VERIFIKASI.md dan PDF untuk urutan yang lengkap.

## Pembelajaran bertahap

03_cloud: 01_https.cpp → 02_payload.cpp → 99_lengkap.cpp. 04_server: 01_teks.cpp → 02_sensor.cpp → 99_lengkap.cpp.

Mulai dari [panduan tahapan](TAHAPAN.md). Kode lengkap dipakai setelah bukti tiap tahap diperiksa; lihat PDF untuk penjelasan konstruksi dan posisi setiap tambahan.

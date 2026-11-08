# API sensor sendiri dengan Laravel dan MySQL

Kode API dan dashboard yang diajarkan di dalam modul pertemuan 9, MK38 Internet of Things. ESP32 mengirim suhu dan kelembapan ke Laravel melalui HTTP POST. Laravel memvalidasi isinya, menyimpan satu baris di MySQL, lalu mengembalikan ID catatan. Mahasiswa membaca ID tersebut kembali melalui HTTP GET dan mencocokkannya dengan tabel database.

Setelah alur dasar lulus, ikuti [dashboard dan kendali secara bertahap](DASHBOARD_BERTAHAP.md). Halaman `/latihan/tabel` memperkenalkan Blade, `/latihan/nilai` membaca satu JSON melalui JavaScript, lalu `/dashboard` menyediakan grafik, pilihan perangkat, CSV, ambang latihan, serta kendali LED dengan konfirmasi ESP32. [Pemetaan proyek akhir](PENGEMBANGAN_PROYEK.md) menjelaskan pemakaian contoh ini pada enam topik brief. Jalankan `php artisan migrate` dari `backend` saat memperbarui lab.

Alur praktik: **DHT22 → ESP32 di Wokwi → API Laravel → MySQL**.

Untuk variasi output, lanjutkan ke [praktik aktuator LED dan servo](AKTUATOR_BERTAHAP.md).
Halaman `/aktuator` membedakan target operator dan laporan firmware,
serta menampilkan riwayat yang disimpan pada tiga tabel MySQL tambahan.
Proyek PlatformIO-nya berada pada `esp32_aktuator`, dengan tiga versi
program dari uji GPIO sampai kendali REST. Jalur ini dapat dijalankan
tanpa mengirim data sensor terlebih dahulu.

Pada edisi terbaru modul 9, Laravel dan MySQL menjadi jalur praktik utama setelah Wi-Fi dan DHT22. ThingSpeak tetap tersedia sebagai pengayaan cloud. PHP, Composer, MySQL, Python, serta pemasangan dependency disiapkan sebelum sesi 150 menit. Sumber pengajar berada di folder `api_sensor`; paket praktik dan GitHub menempatkan salinan kode yang sama pada `pertemuan09/05_api_laravel`. Akar lab adalah folder yang memuat `backend`, `client_python`, dan `esp32`. Jalankan semua skrip Python dari akar ini; perintah lain menyebutkan folder kerjanya.

## Persiapan sebelum kelas

Lokasi kode mengikuti aplikasi yang menjalankannya:

| Jenis | Letak dan tindakan |
|---|---|
| C++ ESP32 | Buka `esp32` sebagai workspace VS Code. Program aktif `esp32/src/main.cpp`; Build melalui PlatformIO, lalu Start Simulator melalui Wokwi. |
| Versi C++ | Salin satu berkas utuh dari `esp32/versi` ke `esp32/src/main.cpp`. Jangan menaruh seluruh versi di `src`, karena `setup()`/`loop()` akan rangkap. |
| Header ESP32 | Sunting berkas bernama `.h` pada `esp32/include`; nama mengikuti `#include` pada program. |
| PHP/Blade/JavaScript | Sunting berkas pada `backend` yang disebutkan langkahnya. Laravel berjalan di laptop dan JavaScript halaman berjalan di browser. |
| Python | Sunting berkas pada `client_python`, lalu jalankan dari akar lab pada terminal B. Python pada laptop menjadi client HTTP. |
| Perintah terminal | Ketik pada terminal A/B atau terminal PlatformIO sesuai folder yang diminta; perintah bukan isi `main.cpp`. |
| SQL | Jalankan pada MySQL Workbench atau klien MySQL yang terhubung. |

Kotak cuplikan menjelaskan bagian tertentu dari berkas yang sudah tersedia.
Jangan menimpa satu berkas utuh dengan beberapa baris cuplikan. Folder
`01`, `02`, dan seterusnya pada paket menandai tahap, bukan nama yang
diwajibkan PlatformIO. Selama mengikuti modul, pertahankan nama folder dan
berkas agar jalur pada perintah tetap cocok.

- PHP 8.2 atau 8.3, Composer 2, serta ekstensi PHP `pdo_mysql`, `mbstring`, `openssl`, `fileinfo`, dan `zip`. Gunakan PHP yang sesuai dengan `composer.lock`; contoh ini memakai Laravel 12. Uji `php -v`, `composer --version`, dan `php -m` dari terminal VS Code.
- MySQL 8.0 atau 8.4 yang sudah berjalan. Uji `mysql --version`. Database bawaan XAMPP umumnya MariaDB; keduanya harus dibedakan ketika menulis laporan hasil uji. Pengujian lab ini memakai MySQL asli.
- VS Code, PlatformIO, dan ekstensi Wokwi yang telah diaktifkan. Gunakan cara aktivasi dari modul utama.
- Python 3.10 atau lebih baru. Skrip memakai pustaka standar Python; tidak ada paket tambahan yang perlu dipasang dengan pip. Periksa `python --version`. Pada Linux/macOS, gunakan `python3` jika itu nama perintah Python 3; pada Windows, `py -3` dapat dipakai jika `python` belum dikenali.
- Dua terminal: A menjalankan Laravel; B menjalankan skrip Python atau perintah persiapan. Buka keduanya dari akar lab. Blok penyalinan berkas di bawah memakai PowerShell pada Windows.

Folder `backend` memuat aplikasi Laravel; `esp32` memuat proyek PlatformIO. Folder `tahapan` menyimpan versi route yang dipakai satu per satu. `bukti` memuat hasil pengujian. Password database dan `APP_KEY` berada pada `.env` lokal; berkas tersebut tidak dibagikan.

Gunakan dua jendela VS Code. Jendela pertama membuka akar lab ini untuk
menyunting backend dan menjalankan terminal A/B. Pilih **File > New Window**,
lalu buka subfolder `esp32` pada jendela kedua untuk PlatformIO dan Wokwi.
Biarkan jendela pertama serta terminal server tetap berjalan. Jangan
mengganti folder pada jendela server saat membuka proyek ESP32.

Khusus Windows dengan PowerShell: jika memakai PHP XAMPP dan perintah `php` belum dikenali, tambahkan folder PHP pada PATH terminal tersebut sebelum menjalankan perintah:

```powershell
$env:Path = 'C:\xampp\php;' + $env:Path
php -v
```

Ulangi pada terminal baru bila diperlukan. Composer dipasang dari [situs resminya](https://getcomposer.org/download/). Server API dijalankan melalui Artisan; Apache tidak diperlukan untuk langkah di bawah.

Perintah `Copy-Item` pada panduan ini khusus PowerShell Windows. Pada Linux/macOS, lakukan penyalinan yang sama melalui Explorer di VS Code: salin berkas sumber, tempel pada folder tujuan, lalu ganti nama berkas hasil salinan sesuai tujuan dan konfirmasi penggantian bila diminta. Contohnya, isi `tahapan/01_api_health.php` menggantikan `backend/routes/api.php`. Perintah `cd`, PHP, Composer, serta PlatformIO tetap dijalankan dari folder yang disebutkan.

### Siapkan konfigurasi client Python

Buka `client_python/konfigurasi.py` di editor VS Code. Pertahankan nilai berikut untuk contoh bawaan:

```python
API_DASAR = "http://127.0.0.1:8000"
ID_SENSOR = "esp32-kelompok-01"
ID_AKTUATOR = "esp32-aktuator-01"
```

`API_DASAR` adalah alamat Laravel dari laptop. Jika port server diganti, samakan angka port pada konfigurasi ini. `ID_SENSOR` harus sama dengan `DEVICE_ID` pada `esp32/include/config.h`; `ID_AKTUATOR` dipakai pada latihan LED dan servo terpisah. Jangan mengubah alamat client laptop menjadi `host.wokwi.internal`; nama host itu dipakai firmware simulator.

Setiap perintah Python berikut dijalankan di terminal B dari akar lab. Simpan perubahan sebelum menjalankannya lagi. Jika memakai `python3` atau `py -3`, ganti bagian `python` pada setiap perintah dengan perintah yang tersedia di komputer Anda. Python membaca berkas terbaru setiap kali dijalankan; langkah Build hanya untuk firmware ESP32.

## 1. Kenali URL dan data yang dipertukarkan

| Metode dan path | Fungsi | Hasil yang diharapkan |
|---|---|---|
| `GET /api/v1/health` | Memeriksa apakah Laravel dapat diakses | 200, `{"status":"ok"}` |
| `POST /api/v1/sensor` | Mengirim satu pembacaan | Tahap 2: 200 tanpa penyimpanan; tahap 3: 201 dan ID catatan |
| `GET /api/v1/sensor` | Membaca 20 catatan terbaru secara bawaan; `limit` dapat diisi 1 sampai 100 | 200, larik JSON; `[]` jika belum ada data |
| `GET /api/v1/sensor/{id}` | Membaca satu catatan | 200; 404 jika ID tidak ditemukan |

Body POST memakai format yang sama dari tahap 2 sampai tahap sensor:

```json
{"device_id":"esp32-kelompok-01","suhu":28.0,"kelembapan":65.0}
```

`device_id` adalah nama perangkat kelompok, maksimal 40 karakter, berupa huruf, angka, `_`, atau `-`; karakter pertama berupa huruf/angka. `suhu` memakai Celsius, rentang latihan mengikuti DHT22 yaitu -40 sampai 80. `kelembapan` memakai persen, 0 sampai 100. MySQL menyimpan kedua angka dengan satu angka desimal. `created_at` adalah waktu penerimaan server dalam UTC, bukan waktu pengukuran ESP32.

`/api` ditambahkan otomatis oleh konfigurasi Laravel. Karena itu, tulis `/v1/sensor` pada `routes/api.php`, lalu akses `/api/v1/sensor` dari klien. Jangan menggandakan awalan menjadi `/api/api/...`.

## 2. Pasang paket dan jalankan satu route

Di terminal B, dari akar lab. Blok penyalinan berikut memakai PowerShell Windows; alternatif Explorer VS Code dijelaskan pada bagian persiapan:

```powershell
cd backend
composer install
Copy-Item .env.example .env
php artisan key:generate
cd ..
Copy-Item tahapan/01_api_health.php backend/routes/api.php
```

Penyalinan `.env` dilakukan pada pemasangan pertama. Jika `.env` sudah diisi, pertahankan isinya. `composer install` memakai versi pada lockfile. Tidak diperlukan npm untuk API ini.

Buka `backend/bootstrap/app.php`. Pada `withRouting`, baris berikut mendaftarkan file API:

```php
api: __DIR__.'/../routes/api.php',
```

Paket telah memuat baris itu. Pada proyek Laravel 12 baru, file API belum tentu tersedia. Menambahkan file saja belum cukup jika belum didaftarkan. Lab ini mendaftarkannya langsung; autentikasi Sanctum belum digunakan.

Baca `tahapan/01_api_health.php`: `Route::get` menyambungkan satu path dengan fungsi yang mengembalikan JSON. Jalankan di terminal A:

```powershell
cd backend
php artisan serve --host=127.0.0.1 --port=8000
```

Biarkan terminal A berjalan. Buka `client_python/01_health.py` sebelum menjalankannya: `urlopen()` meminta URL health, lalu kode membaca respons dan JSON. Tidak ada nilai yang perlu diubah pada skrip ini; alamat berasal dari `konfigurasi.py`. Di terminal B, dari akar lab:

```sh
python client_python/01_health.py
```

Hasil normal menampilkan `HTTP 200` dan nilai `status` berupa `ok`. Jika muncul `Health gagal`, periksa terminal A dan `API_DASAR`, lalu jalankan skrip yang sama. Status 404 berarti path atau route belum sesuai; periksa salinan route health sebelum lanjut. `GET /api/v1/sensor` pada tahap ini masih 404 karena route-nya belum dibuat. Tabel MySQL belum diperlukan.

## 3. Terima JSON tanpa menyimpannya

Di terminal B, dari akar lab, ganti file route. Blok berikut untuk PowerShell Windows; di sistem lain salin melalui Explorer VS Code:

```powershell
Copy-Item tahapan/02_api_terima.php backend/routes/api.php
```

Tambahan pada versi ini adalah `Route::post`, objek `Request`, dan aturan `validate`. Baris `response()->json` mengembalikan data yang lolos pemeriksaan. Belum ada perintah menulis database.

Sekarang buka `client_python/02_kirim_sensor.py`. Baca `DATA`, pembentukan JSON dengan `json.dumps()`, pengubahan teks menjadi byte UTF-8, header JSON, lalu `Request(..., method="POST")`. `HTTPError` tetap dibaca agar kode status dan alasan penolakan terlihat. Nilai awalnya:

```python
DATA = {"device_id": ID_SENSOR, "suhu": 28.0, "kelembapan": 65.0}
```

Dari akar lab, jalankan:

```sh
python client_python/02_kirim_sensor.py
```

Hasil normal menampilkan `HTTP 200`, objek `diterima`, dan `tersimpan: false`. Ubah hanya nilai `kelembapan` di dalam `DATA` menjadi `101`, simpan, lalu jalankan skrip yang sama. Hasil yang dicari adalah `HTTP 422` dengan objek `errors`; skrip selesai dengan kode gagal karena input sengaja salah. Belum ada INSERT MySQL pada tahap ini.

Sesudah mencatat penolakan, pulihkan `kelembapan` menjadi `65.0`, simpan, dan jalankan lagi sampai kembali diterima. Jika muncul `Koneksi gagal`, hidupkan server atau perbaiki URL sebelum mengulang. Jika respons bukan JSON, periksa path dan log Laravel; jangan menganggap pesan itu bukti penyimpanan.

## 4. Siapkan MySQL dan konfigurasi Laravel

Masuk ke MySQL sebagai administrator melalui MySQL Workbench atau klien `mysql -u root -p`. Buat database dan pengguna khusus lab:

```sql
CREATE DATABASE IF NOT EXISTS mk38_sensor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'mk38_sensor'@'localhost' IDENTIFIED BY 'ganti_password_praktikum';
GRANT ALL PRIVILEGES ON mk38_sensor.* TO 'mk38_sensor'@'localhost';
```

Ganti password contoh pada SQL sebelum dijalankan. Jika pengguna sudah ada, `CREATE USER IF NOT EXISTS` tidak mengganti password-nya; gunakan password yang sudah berlaku. Perintah hanya memberi hak pada database lab tersebut.

Di `backend/.env`, isi enam nilai berikut sesuai server kelompok:

```dotenv
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=mk38_sensor
DB_USERNAME=mk38_sensor
DB_PASSWORD=ISI_PASSWORD_DATABASE
```

Port 3306 adalah contoh. Jika server memakai port lain, samakan `DB_PORT`; pengujian dosen dapat memakai port terpisah. Di terminal B:

```powershell
cd backend
php artisan config:clear
php artisan migrate
php artisan migrate:status
cd ..
```

Jika Artisan menawarkan pembuatan database, periksa kembali tahap SQL terlebih dahulu. Sebelum lanjut: migration `create_sensors_table` berstatus `Ran`. Di MySQL, jalankan `USE mk38_sensor;` lalu `DESCRIBE sensors;`. Kolom `id`, `device_id`, `suhu`, `kelembapan`, `created_at`, dan `updated_at` harus ada.

## 5. Hubungkan request, model, dan tabel

Baca berkas berikut secara berurutan, sebelum memakai route lengkap:

1. `database/migrations/2026_11_06_000001_create_sensors_table.php`: menetapkan nama tabel dan tipe kolom. `up` membuat tabel; `down` membatalkannya.
2. `app/Models/Sensor.php`: menghubungkan model `Sensor` ke tabel `sensors`. `$fillable` membatasi kolom yang boleh diisi dari input; `casts` membuat angka pada JSON tetap berupa angka.
3. `app/Http/Requests/StoreSensorRequest.php`: memindahkan aturan validasi tahap 2 ke satu kelas. `authorize()` bernilai true untuk lab lokal tanpa login.
4. `app/Http/Controllers/SensorController.php`, metode `store`: `validated()` mengambil input yang lolos aturan, `create()` menulis ke MySQL, lalu `refresh()` membaca nilai yang benar-benar disimpan, termasuk pembulatan desimal.
5. Pada controller yang sama, `index` membaca daftar terbaru dan `show` membaca satu ID. Batas `limit` adalah 1 sampai 100 agar permintaan daftar mempunyai batas yang jelas.

Aktifkan versi ketiga di terminal B:

Blok penyalinan berikut memakai PowerShell Windows. Di Linux/macOS, ganti berkas route melalui Explorer VS Code, lalu jalankan perintah PHP dari folder yang sama.

```powershell
Copy-Item tahapan/03_api_mysql.php backend/routes/api.php
cd backend
php artisan route:list --path=api
cd ..
```

### Baca fungsi HTTP bersama sebelum memakainya

Buka seluruh `client_python/http_json.py`. Fungsi `minta(metode, path, payload=None)` memindahkan pekerjaan HTTP yang baru dipelajari pada skrip 02 ke satu tempat. Telusuri urutannya: payload menjadi byte JSON bila ada, `Request` menggabungkan `API_DASAR` dengan path, `urlopen()` memakai timeout sepuluh detik, lalu kode membaca respons normal maupun `HTTPError`. Fungsi mencetak metode, path, HTTP, serta JSON dan mengembalikan pasangan `status, data`.

Kode HTTP 422/404/500 tetap dikembalikan kepada pemanggil agar skrip dapat menentukan langkah berikutnya. Kegagalan koneksi atau respons yang bukan JSON menghentikan program dengan pesan. Baca penanganan ini sebelum membuka `03_simpan_baca.py`; jangan menyalin fungsi yang sama ke setiap skrip.

### Simpan satu catatan dan baca ID yang sama

Buka `client_python/03_simpan_baca.py`. Pastikan `DATA` berisi kelembapan `65.0` dan `ID_SENSOR` pada konfigurasi sudah benar. Skrip memanggil `minta()` untuk POST, mengambil `id` hasil simpan, lalu GET ID itu. Jalankan dari akar lab:

```sh
python client_python/03_simpan_baca.py
```

Hasil normal menampilkan POST HTTP 201, GET HTTP 200, serta pesan bahwa keduanya membaca catatan yang sama. Perbandingan memakai seluruh JSON hasil simpan, termasuk angka yang sudah dibulatkan MySQL. Jika muncul `Belum tersimpan`, baca kode HTTP dan JSON sebelumnya: aktifkan route tahap 3, pulihkan data bila 422, atau perbaiki koneksi MySQL bila 500. Jika GET belum cocok, periksa respons dan log sebelum lanjut.

Setiap menjalankan skrip 03 membuat POST baru. Gunakan skrip 04 pada tahap berikutnya bila hanya ingin membaca catatan. Di MySQL, periksa hasil simpan secara terpisah:

```sql
SELECT id, device_id, suhu, kelembapan, created_at FROM sensors ORDER BY id DESC LIMIT 5;
```

Ini pemeriksaan penyimpanan yang terpisah dari pesan berhasil pada ESP32. Permintaan POST berikutnya membuat catatan baru. Lab ini belum memakai ID kiriman untuk mencegah duplikasi ketika mencoba ulang.

## 6. Hubungkan ESP32: periksa health terlebih dahulu

Buka **folder `esp32`** sebagai workspace VS Code karena folder itulah yang berisi `platformio.ini` dan `wokwi.toml`. Terminal backend A tetap berjalan pada folder `backend`.

Di `esp32/include/config.h`, periksa:

```cpp
const char* API_BASE = "http://host.wokwi.internal:8000";
```

Dari browser atau client Python laptop, alamatnya `http://127.0.0.1:8000`. Dari ESP32 simulasi, alamat laptop adalah `host.wokwi.internal`. `localhost` di dalam ESP32 merujuk ke ESP32 itu sendiri. Jangan menaruh port MySQL 3306 pada URL API; ESP32 berbicara dengan Laravel pada port 8000.

Gunakan Wokwi **di VS Code**, yang menyertakan gateway lokal. Public Gateway Wokwi web tidak dapat menjangkau server laptop. Konfigurasi penerusan `localhost:8180` dari proyek server ESP32 sebelumnya tidak dipakai di sini karena ESP32 sekarang menjadi klien.

Di terminal PlatformIO, dari folder `esp32`. Blok penyalinan berikut memakai PowerShell Windows; alternatifnya, salin berkas versi melalui Explorer VS Code:

```powershell
Copy-Item versi/01_health.cpp src/main.cpp
pio run
```

Jalankan `Wokwi: Start Simulator` dari F1. Serial harus menampilkan `GET /api/v1/health -> 200` dan `{"status":"ok"}`. Jika nilainya negatif, periksa URL, port, dan proses Laravel sebelum menambahkan pembacaan sensor.

## 7. Kirim angka tetap dari ESP32

Hentikan simulator. Dari folder `esp32`, gunakan PowerShell Windows atau salin berkas versi melalui Explorer VS Code:

```powershell
Copy-Item versi/02_kirim_contoh.cpp src/main.cpp
pio run
```

Mulai kembali simulator. Versi ini menambahkan body JSON serta header `Content-Type: application/json` dan `Accept: application/json`. `http.POST(body)` mengirim permintaan; angka pada body belum berasal dari DHT22.

Sebelum lanjut: Serial menampilkan `POST contoh -> 201`. Baca kembali ID dari laptop dan periksa MySQL. Ganti `DEVICE_ID` di `include/config.h` dengan nama kelompok, menggunakan karakter yang diterima aturan validasi.

## 8. Ganti angka tetap dengan DHT22

Hentikan simulator. Dari folder `esp32`, gunakan PowerShell Windows atau salin berkas versi melalui Explorer VS Code:

```powershell
Copy-Item versi/03_sensor.cpp src/main.cpp
pio run
```

Versi ini menambahkan `DHTesp`, inisialisasi GPIO 15, dan `getTempAndHumidity()`. Bagian pembentukan JSON mengambil `data.temperature` dan `data.humidity`, masing-masing satu angka desimal. Pembacaan gagal dilewati. Firmware memberi jeda lima detik setelah setiap permintaan; timeout koneksi dan baca membatasi waktu tunggu.

Mulai kembali simulator. Klik DHT22, ubah suhu dan kelembapan, lalu tunggu kiriman berikutnya. Coba 28/65, 32/70, dan 35/75. Untuk membaca kiriman dari laptop, buka `client_python/04_baca_sensor.py`: `urlencode()` menyusun filter dari `ID_SENSOR` dan batas lima catatan. Jika ID firmware diubah, samakan `ID_SENSOR` dalam `client_python/konfigurasi.py`. Jalankan di terminal B dari akar lab:

```sh
python client_python/04_baca_sensor.py
```

Hasil normal adalah GET HTTP 200 dan larik maksimal lima catatan untuk ID itu, terbaru lebih dahulu. Larik `[]` berarti belum ada kiriman untuk ID tersebut; periksa ejaan ID dan tunggu POST firmware 201 sebelum mengulang. Jika HTTP bukan 200 atau koneksi gagal, pulihkan server, route tahap 3, atau MySQL sesuai pesan. Jangan menjalankan skrip 03 untuk memperbaiki hasil kosong karena itu akan membuat data laptop baru.

Pastikan ketiga pasangan nilai muncul pada GET dan MySQL. Karena batasnya lima catatan terbaru, baca segera setelah setiap perubahan dan catat ID yang sesuai. Untuk memeriksa data setelah restart, hentikan simulator dahulu dan catat ID hasil skrip 04. Hentikan Laravel dengan Ctrl+C, jalankan kembali perintah `php artisan serve --host=127.0.0.1 --port=8000` di terminal A yang masih berada di `backend`, lalu ulangi skrip 04. ID lama harus tetap ada. Mulai kembali simulator setelah pemeriksaan selesai.

## 9. Bukti dan diagnosis

Kumpulkan satu respons 201 lengkap, GET ID yang sama, hasil SELECT MySQL, tiga pasangan DHT22 yang berbeda, serta satu respons 422. Catat versi PHP, Laravel, dan MySQL. Screenshot harus menunjukkan langkah dan hasil; samarkan password serta `APP_KEY`.

| Gejala | Pemeriksaan berikutnya |
|---|---|
| `python` tidak dikenali atau versinya terlalu lama | Gunakan Python 3.10 atau lebih baru; coba `python3` pada Linux/macOS atau `py -3` pada Windows sesuai pemasangan. |
| Skrip atau `konfigurasi` tidak ditemukan | Jalankan perintah Python dari akar lab dan pertahankan susunan berkas `client_python`; mulai ulang pemeriksaan dengan `python client_python/01_health.py`. |
| Client menampilkan koneksi gagal | Periksa terminal A, `API_DASAR`, dan port; ulangi skrip health sebelum melanjutkan. |
| `php` atau `composer` tidak dikenali | Periksa pemasangan dan PATH terminal yang sedang dipakai. |
| `could not find driver` | Periksa `php -m`; `pdo_mysql` harus aktif pada PHP CLI yang sama. |
| SQLSTATE 1045 / access denied | Samakan pengguna dan password di `.env`; jalankan `config:clear`. |
| SQLSTATE 1049 / unknown database | Buat `mk38_sensor` pada server/port yang tercantum di `.env`. |
| Tabel `sensors` belum ada | Jalankan `migrate` dan periksa `migrate:status`. |
| 404 pada seluruh `/api/...` | Periksa baris `api:` di `bootstrap/app.php` dan `route:list`. |
| 419 saat POST | Route kemungkinan diletakkan pada middleware web. Gunakan `routes/api.php`; jangan mematikan CSRF seluruh aplikasi. |
| 422 | Baca objek `errors`; samakan nama field dan rentang angkanya. |
| ESP32 mendapat status negatif | Pastikan API hidup, port benar, hostname `host.wokwi.internal`, dan Wokwi VS Code aktif. |
| 201 tetapi tabel yang dilihat kosong | Cocokkan host, port, nama database, dan ID; periksa server yang benar. |

## Lanjutan client Python untuk aktuator

Ikuti [praktik aktuator LED dan servo](AKTUATOR_BERTAHAP.md) untuk menyiapkan tiga tabel tambahan serta workspace `esp32_aktuator`. Jalur ini memakai `ID_AKTUATOR` pada `client_python/konfigurasi.py`, yang harus sama dengan `DEVICE_ID` pada `esp32_aktuator/include/config.h`. Baca juga seluruh `client_python/aktuator.py` sebelum skrip 08: fungsi `cari_id(nama)` meminta daftar sesuai ID perangkat, lalu mengambil ID numerik dari baris bernama `lampu` atau `pintu`. Jika nama belum terdaftar, fungsi menghentikan program dan meminta pendaftaran melalui skrip 06 atau 07.

Perintah berikut tetap dijalankan dari akar lab pada terminal B, pada langkah yang sesuai dalam panduan aktuator. Kolom perubahan menyebut bagian yang dibuka di editor; simpan sebelum menjalankan ulang.

| Perintah | Bagian yang diperiksa/diubah | Hasil normal | Jika gagal dan cara memulihkan |
|---|---|---|---|
| `python client_python/06_daftar_led.py` | Periksa `ID_AKTUATOR`; pertahankan `name="lampu"` dan `kind="led"` agar sesuai firmware. | POST 201 pada pendaftaran pertama, atau 200 dengan ID sama saat diulang. | Jika 409, identitas itu sudah memakai jenis berbeda; pulihkan ID/nama sesuai konfigurasi latihan. Jika koneksi gagal, pulihkan server dan ulangi health. |
| `python client_python/07_daftar_servo.py` | Periksa ID yang sama; pertahankan `name="pintu"` dan `kind="servo"`. | POST 201/200, lalu GET 200 yang memuat kedua aktuator. | Jika daftar tidak sesuai, samakan ID konfigurasi dengan firmware dan ulangi pendaftaran yang benar; 409 meminta pemeriksaan identitas/jenis. |
| `python client_python/08_target_led.py` | `NILAI = 1` untuk nyala; ubah menjadi `0` untuk mati. | POST 202 dan GET riwayat 200; target tercatat, konfirmasi menunggu firmware. | Jika nama tidak ditemukan, jalankan skrip 06; nilai selain 0/1 ditolak. Pulihkan `NILAI = 1` untuk mengulang contoh nyala. Setiap menjalankan skrip membuat perintah baru. |
| `python client_python/09_baca_aktuator.py` | Tidak ada nilai yang perlu diubah; skrip membaca `lampu` dan `pintu` sesuai `ID_AKTUATOR`. | GET perintah dan riwayat 200 untuk keduanya; `command:null` berarti tidak ada pending yang masih berlaku. | Jika nama tidak ditemukan, selesaikan skrip 06/07; jika koneksi gagal, pulihkan API lalu ulangi skrip baca ini. |
| `python client_python/10_servo.py` | `SUDUT = 90`; coba 0, 90, lalu 180 satu per satu. | POST 202 dengan ID perintah baru; tunggu konfirmasi firmware sebelum sudut berikutnya. | Jika nama belum ada, jalankan skrip 07; jika 422, pulihkan sudut ke bilangan bulat 0 sampai 180. Kembalikan ke 90 untuk mengulang contoh. |
| `python client_python/11_uji_servo_salah.py` | Pertahankan payload `value:181`; masukan ini sengaja salah. | HTTP 422 dan pesan bahwa nilai di luar rentang ditolak; tidak ada perintah baru. | Jika status lain, periksa daftar aktuator, route, dan API. Tidak ada konfigurasi valid yang perlu dipulihkan pada skrip ini; gunakan skrip 10 dengan sudut valid setelah uji. |

Skrip 08 dan 10 mengirim target; gunakan skrip 09 untuk membaca ulang tanpa membuat perintah. Konfirmasi servo berasal dari nilai PWM yang dilaporkan firmware, tanpa sensor posisi mekanis.

## Pengembangan setelah alur lokal lulus

API awal ini berjalan pada loopback laptop tanpa login. Sebelum dipindahkan ke server internet, tambahkan autentikasi perangkat, HTTPS dengan pemeriksaan sertifikat, pembatasan kiriman, dan aturan akses antarkelompok. Materi TLS dapat dihubungkan dengan pertemuan 13. Menambahkan endpoint LED atau dashboard sebaiknya dilakukan setelah bukti penyimpanan sensor lulus.

Rujukan: [route API Laravel 12](https://laravel.com/docs/12.x/routing), [validasi](https://laravel.com/docs/12.x/validation), [migration](https://laravel.com/docs/12.x/migrations), [Eloquent](https://laravel.com/docs/12.x/eloquent), serta [gateway Wokwi VS Code](https://docs.wokwi.com/vscode/project-config#iot-gateway-esp32-wifi).

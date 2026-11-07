# API sensor sendiri dengan Laravel dan MySQL

Kode API dan dashboard yang diajarkan di dalam modul pertemuan 9, MK38 Internet of Things. ESP32 mengirim suhu dan kelembapan ke Laravel melalui HTTP POST. Laravel memvalidasi isinya, menyimpan satu baris di MySQL, lalu mengembalikan ID catatan. Mahasiswa membaca ID tersebut kembali melalui HTTP GET dan mencocokkannya dengan tabel database.

Setelah alur dasar lulus, ikuti [dashboard dan kendali secara bertahap](DASHBOARD_BERTAHAP.md). Halaman `/latihan/tabel` memperkenalkan Blade, `/latihan/nilai` membaca satu JSON melalui JavaScript, lalu `/dashboard` menyediakan grafik, pilihan perangkat, CSV, ambang latihan, serta kendali LED dengan konfirmasi ESP32. [Pemetaan proyek akhir](PENGEMBANGAN_PROYEK.md) menjelaskan pemakaian contoh ini pada enam topik brief. Jalankan `php artisan migrate` dari `backend` saat memperbarui lab.

Alur praktik: **DHT22 → ESP32 di Wokwi → API Laravel → MySQL**.

Pada edisi terbaru modul 9, Laravel dan MySQL menjadi jalur praktik utama setelah Wi-Fi dan DHT22. ThingSpeak tetap tersedia sebagai pengayaan cloud. PHP, Composer, MySQL, serta pemasangan dependency disiapkan sebelum sesi 150 menit. Sumber pengajar berada di folder `api_sensor`; paket praktik dan GitHub menempatkan salinan kode yang sama pada `pertemuan09/05_api_laravel`. Semua perintah berikut dijalankan dari akar folder lab tersebut.

## Persiapan sebelum kelas

Lokasi kode mengikuti aplikasi yang menjalankannya:

| Jenis | Letak dan tindakan |
|---|---|
| C++ ESP32 | Buka `esp32` sebagai workspace VS Code. Program aktif `esp32/src/main.cpp`; Build melalui PlatformIO, lalu Start Simulator melalui Wokwi. |
| Versi C++ | Salin satu berkas utuh dari `esp32/versi` ke `esp32/src/main.cpp`. Jangan menaruh seluruh versi di `src`, karena `setup()`/`loop()` akan rangkap. |
| Header ESP32 | Sunting berkas bernama `.h` pada `esp32/include`; nama mengikuti `#include` pada program. |
| PHP/Blade/JavaScript | Sunting berkas pada `backend` yang disebutkan langkahnya. Laravel berjalan di laptop dan JavaScript halaman berjalan di browser. |
| Perintah PowerShell | Ketik pada terminal A/B atau terminal PlatformIO sesuai folder yang diminta; perintah bukan isi `main.cpp`. |
| SQL | Jalankan pada MySQL Workbench atau klien MySQL yang terhubung. |

Kotak cuplikan menjelaskan bagian tertentu dari berkas yang sudah tersedia.
Jangan menimpa satu berkas utuh dengan beberapa baris cuplikan. Folder
`01`, `02`, dan seterusnya pada paket menandai tahap, bukan nama yang
diwajibkan PlatformIO. Selama mengikuti modul, pertahankan nama folder dan
berkas agar jalur pada perintah tetap cocok.

- PHP 8.2 atau 8.3, Composer 2, serta ekstensi PHP `pdo_mysql`, `mbstring`, `openssl`, `fileinfo`, dan `zip`. Gunakan PHP yang sesuai dengan `composer.lock`; contoh ini memakai Laravel 12. Uji `php -v`, `composer --version`, dan `php -m` dari terminal VS Code.
- MySQL 8.0 atau 8.4 yang sudah berjalan. Uji `mysql --version`. Database bawaan XAMPP umumnya MariaDB; keduanya harus dibedakan ketika menulis laporan hasil uji. Pengujian lab ini memakai MySQL asli.
- VS Code, PlatformIO, dan ekstensi Wokwi yang telah diaktifkan. Gunakan cara aktivasi dari modul utama.
- Dua terminal PowerShell: A menjalankan Laravel; B mengirim permintaan atau menjalankan perintah persiapan. Buka keduanya di folder `api_sensor` yang telah diekstrak.

Folder `backend` memuat aplikasi Laravel; `esp32` memuat proyek PlatformIO. Folder `tahapan` menyimpan versi route yang dipakai satu per satu. `bukti` memuat hasil pengujian. Password database dan `APP_KEY` berada pada `.env` lokal; berkas tersebut tidak dibagikan.

Gunakan dua jendela VS Code. Jendela pertama membuka akar lab ini untuk
menyunting backend dan menjalankan terminal A/B. Pilih **File > New Window**,
lalu buka subfolder `esp32` pada jendela kedua untuk PlatformIO dan Wokwi.
Biarkan jendela pertama serta terminal server tetap berjalan. Jangan
mengganti folder pada jendela server saat membuka proyek ESP32.

Jika memakai PHP XAMPP dan perintah `php` belum dikenali, tambahkan folder PHP pada PATH **terminal tersebut** sebelum menjalankan perintah:

```powershell
$env:Path = 'C:\xampp\php;' + $env:Path
php -v
```

Ulangi pada terminal baru bila diperlukan. Composer dipasang dari [situs resminya](https://getcomposer.org/download/). Server API dijalankan melalui Artisan; Apache tidak diperlukan untuk langkah di bawah.

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

Di terminal B, dari folder `api_sensor`:

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

Biarkan terminal A berjalan. Di terminal B, yang tetap berada di `api_sensor`:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
```

Sebelum lanjut: pastikan nilai `status` adalah `ok`. `GET /api/v1/sensor` pada tahap ini masih 404 karena route-nya belum dibuat. Tabel MySQL belum diperlukan.

## 3. Terima JSON tanpa menyimpannya

Di terminal B, ganti file route:

```powershell
Copy-Item tahapan/02_api_terima.php backend/routes/api.php
```

Tambahan pada versi ini adalah `Route::post`, objek `Request`, dan aturan `validate`. Baris `response()->json` mengembalikan data yang lolos pemeriksaan. Belum ada perintah menulis database.

```powershell
$data = @{device_id='esp32-kelompok-01'; suhu=28.0; kelembapan=65.0} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/v1/sensor -Method Post -ContentType 'application/json' -Body $data
```

Sebelum lanjut: respons memuat `diterima` dan `tersimpan: false`. Coba `kelembapan=101`: server harus menolak dengan 422. Pada PowerShell 5, respons 422 ditampilkan sebagai error perintah; itu adalah hasil uji input salah yang memang diharapkan. Nilai tersebut tidak boleh dianggap berhasil dikirim.

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

```powershell
Copy-Item tahapan/03_api_mysql.php backend/routes/api.php
cd backend
php artisan route:list --path=api
cd ..
```

Jalankan POST pada tahap 3 sekali lagi. Respons kini memuat `id`, `device_id`, nilai sensor, dan `created_at`. Untuk melihat kode status secara langsung:

```powershell
$hasil = Invoke-WebRequest http://127.0.0.1:8000/api/v1/sensor -Method Post -ContentType 'application/json' -Body $data -UseBasicParsing
$hasil.StatusCode
$catatan = $hasil.Content | ConvertFrom-Json
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/sensor/$($catatan.id)"
```

Sebelum lanjut: status POST harus 201; GET harus menampilkan ID dan nilai yang sama. Di MySQL:

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

Dari browser/PowerShell laptop, alamatnya `http://127.0.0.1:8000`. Dari ESP32 simulasi, alamat laptop adalah `host.wokwi.internal`. `localhost` di dalam ESP32 merujuk ke ESP32 itu sendiri. Jangan menaruh port MySQL 3306 pada URL API; ESP32 berbicara dengan Laravel pada port 8000.

Gunakan Wokwi **di VS Code**, yang menyertakan gateway lokal. Public Gateway Wokwi web tidak dapat menjangkau server laptop. Konfigurasi penerusan `localhost:8180` dari proyek server ESP32 sebelumnya tidak dipakai di sini karena ESP32 sekarang menjadi klien.

Di terminal PlatformIO, dari folder `esp32`:

```powershell
Copy-Item versi/01_health.cpp src/main.cpp
pio run
```

Jalankan `Wokwi: Start Simulator` dari F1. Serial harus menampilkan `GET /api/v1/health -> 200` dan `{"status":"ok"}`. Jika nilainya negatif, periksa URL, port, dan proses Laravel sebelum menambahkan pembacaan sensor.

## 7. Kirim angka tetap dari ESP32

Hentikan simulator. Dari folder `esp32`:

```powershell
Copy-Item versi/02_kirim_contoh.cpp src/main.cpp
pio run
```

Mulai kembali simulator. Versi ini menambahkan body JSON serta header `Content-Type: application/json` dan `Accept: application/json`. `http.POST(body)` mengirim permintaan; angka pada body belum berasal dari DHT22.

Sebelum lanjut: Serial menampilkan `POST contoh -> 201`. Baca kembali ID dari laptop dan periksa MySQL. Ganti `DEVICE_ID` di `include/config.h` dengan nama kelompok, menggunakan karakter yang diterima aturan validasi.

## 8. Ganti angka tetap dengan DHT22

Hentikan simulator. Dari folder `esp32`:

```powershell
Copy-Item versi/03_sensor.cpp src/main.cpp
pio run
```

Versi ini menambahkan `DHTesp`, inisialisasi GPIO 15, dan `getTempAndHumidity()`. Bagian pembentukan JSON mengambil `data.temperature` dan `data.humidity`, masing-masing satu angka desimal. Pembacaan gagal dilewati. Firmware memberi jeda lima detik setelah setiap permintaan; timeout koneksi dan baca membatasi waktu tunggu.

Mulai kembali simulator. Klik DHT22, ubah suhu dan kelembapan, lalu tunggu kiriman berikutnya. Coba 28/65, 32/70, dan 35/75. Dari laptop:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/v1/sensor?device_id=esp32-kelompok-01&limit=5'
```

Sebelum lanjut: ketiga pasangan nilai muncul pada respons dan tabel MySQL. Hentikan Laravel dengan Ctrl+C, mulai lagi, lalu baca ID lama: data harus tetap ada. Keberhasilan koneksi Wi-Fi saja belum membuktikan data tersimpan.

## 9. Bukti dan diagnosis

Kumpulkan satu respons 201 lengkap, GET ID yang sama, hasil SELECT MySQL, tiga pasangan DHT22 yang berbeda, serta satu respons 422. Catat versi PHP, Laravel, dan MySQL. Screenshot harus menunjukkan langkah dan hasil; samarkan password serta `APP_KEY`.

| Gejala | Pemeriksaan berikutnya |
|---|---|
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

## Pengembangan setelah alur lokal lulus

API awal ini berjalan pada loopback laptop tanpa login. Sebelum dipindahkan ke server internet, tambahkan autentikasi perangkat, HTTPS dengan pemeriksaan sertifikat, pembatasan kiriman, dan aturan akses antarkelompok. Materi TLS dapat dihubungkan dengan pertemuan 13. Menambahkan endpoint LED atau dashboard sebaiknya dilakukan setelah bukti penyimpanan sensor lulus.

Rujukan: [route API Laravel 12](https://laravel.com/docs/12.x/routing), [validasi](https://laravel.com/docs/12.x/validation), [migration](https://laravel.com/docs/12.x/migrations), [Eloquent](https://laravel.com/docs/12.x/eloquent), serta [gateway Wokwi VS Code](https://docs.wokwi.com/vscode/project-config#iot-gateway-esp32-wifi).

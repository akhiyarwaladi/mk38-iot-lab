# Aktuator melalui REST: LED, servo, dan riwayat MySQL

Lanjutan praktikum pertemuan 9, MK38 Internet of Things. Selesaikan pemasangan Laravel/MySQL pada README dan latihan dashboard terlebih dahulu. Alokasikan sesi pengayaan tersendiri setelah alur sensor dipahami. Pada praktik ini, operator mengirim perintah dari browser; ESP32 mengambilnya, mengubah output, lalu mengonfirmasi. Laravel menyimpan target, laporan firmware, dan riwayat secara terpisah.

Hasil akhir: LED dapat dinyalakan/dimatikan dan servo dapat diberi sudut 0 sampai 180° melalui halaman `http://127.0.0.1:8000/aktuator`. Setiap perintah mempunyai ID yang dapat ditelusuri dari dashboard ke Serial Monitor, API, dan tabel MySQL. Konfirmasi servo menunjukkan nilai yang ditetapkan melalui PWM oleh firmware. Tidak ada sensor posisi mekanis pada rangkaian ini.

## 1. Siapkan aplikasi, dua terminal, dan rangkaian

Gunakan PHP/Composer/MySQL yang sudah dipasang sesuai README. Tetap jalankan MySQL. Tidak perlu membuat akun atau API key untuk Laravel lokal. API latihan ini belum memakai autentikasi; server hanya dibuka pada `127.0.0.1`.

Terminal A menjalankan server. Terminal B menjalankan klien Python yang sudah tersedia pada `client_python`. Gunakan Python 3.10 atau lebih baru; semua modul yang diimpor berasal dari pustaka standar, sehingga tidak perlu pip install. Dari akar lab, periksa `python --version`; gunakan `python3` pada Linux/macOS atau `py -3` pada Windows bila itu nama perintah yang tersedia. Ganti awalan `python` secara konsisten pada contoh berikut. Keduanya dibuka dari akar lab, yaitu folder yang memuat `backend`, `esp32`, dan `esp32_aktuator`. Di paket GitHub, akar tersebut bernama `pertemuan09/05_api_laravel`. Perintah shell diketik pada terminal; kode PHP/C++/Python disunting pada berkas yang disebutkan. Kotak `Copy-Item` khusus PowerShell Windows. Pada Linux/macOS, salin versi yang disebutkan melalui Explorer VS Code ke `src/main.cpp`, mengganti versi lama, lalu jalankan `pio run`. Jangan menyimpan beberapa versi yang mempunyai `setup()`/`loop()` di folder `src`.

| Berkas/folder | Kegunaan |
|---|---|
| `backend/database/migrations/2026_11_08_000003_create_actuator_tables.php` | Membuat tiga tabel tambahan; bergantung pada tabel `devices` dari migration sebelumnya |
| `backend/app/Models/Actuator.php`, `ActuatorCommand.php`, `ActuatorStateEvent.php` | Model baris pada tiga tabel tersebut |
| `backend/app/Http/Controllers/ActuatorController.php` | Pendaftaran, validasi, perintah, laporan, dan riwayat |
| `backend/routes/actuators.php` | Daftar endpoint aktuator |
| `backend/app/Providers/ActuatorServiceProvider.php` dan `backend/bootstrap/providers.php` | Mendaftarkan route tambahan, termasuk `/aktuator` |
| `backend/resources/views/actuators.blade.php` | Struktur halaman browser |
| `backend/public/actuators.js` dan `actuators.css` | Permintaan HTTP serta tampilan halaman; memakai warna/komponen `dashboard.css` |
| `esp32_aktuator/include/config.h` | URL API dan nama ESP32 |
| `esp32_aktuator/include/actuator_client.h` | Fungsi HTTP dan urutan pendaftaran/pengambilan/konfirmasi |
| `esp32_aktuator/versi` | Tiga program utuh untuk `src/main.cpp`, dipakai bergantian |

Buka jendela VS Code kedua melalui **File > New Window > Open Folder**, lalu pilih `esp32_aktuator`. Pertahankan terminal Laravel pada jendela pertama. Diagram yang disediakan menghubungkan GPIO23 ke resistor 220 ohm dan anoda LED, katoda ke GND; GPIO18 ke PWM servo, VIN ke V+, dan GND ke GND servo. Sambungan VIN ini untuk rangkaian Wokwi. Untuk perangkat fisik, siapkan suplai 5 V yang sesuai kebutuhan servo dengan GND bersama; jangan menyuplai motor dari GPIO.

## 2. Tambahkan tabel tanpa menghapus data sensor

Di terminal B, dari akar lab:

```powershell
cd backend
php artisan migrate
php artisan migrate:status
cd ..
```

Hasil yang dicari: migration `create_actuator_tables` berstatus `Ran`. Jika belum ada tabel `devices`, jalankan seluruh migration bawaan lab dalam urutan normal. Jangan memakai `migrate:fresh` pada database yang berisi bukti sensor, karena perintah itu menghapus tabel.

| Tabel | Yang disimpan |
|---|---|
| `actuators` | Identitas output, jenis, `requested_value`, `reported_value`, sesi boot, urutan dan waktu laporan terakhir |
| `actuator_commands` | Setiap permintaan operator: nilai, status, batas berlaku 30 detik, waktu konfirmasi |
| `actuator_state_events` | Riwayat boot, penerapan perintah, serta perubahan nilai yang dilaporkan |

`requested_value` adalah target terakhir yang diminta operator. `reported_value` adalah nilai terakhir yang dilaporkan firmware. Nilai awal `null` berarti **belum ada**; jangan menyamakannya dengan LED mati atau servo 0°. Tabel sensor tetap dipakai untuk pembacaan DHT22, bukan untuk mencampur perintah aktuator.

Jika server belum berjalan, di terminal A:

```powershell
cd backend
php artisan serve --host=127.0.0.1 --port=8000
```

Di terminal B dari akar lab, jalankan `python client_python/01_health.py`. Hasilnya harus HTTP 200 dan `status` bernilai `ok`. Pada `client_python/konfigurasi.py`, samakan `API_DASAR` dengan alamat Laravel laptop dan `ID_AKTUATOR` dengan `esp32-aktuator-01`. ID ini berbeda dari `ID_SENSOR` pada latihan DHT22.

Sebelum POST pertama, telusuri backend yang sudah disediakan. Baca migration: tabel `actuators` menunjuk `devices` melalui `device_id`; dua tabel riwayat menunjuk ID numerik aktuator. Buka tiga model pada `backend/app/Models`. `casts()` mengembalikan nilai sebagai bilangan bulat dan timestamp sebagai tanggal; model event hanya mempunyai `created_at`, sehingga `UPDATED_AT` dinonaktifkan. Laravel mengisi waktu event dalam UTC agar sesuai waktu konfirmasi.

Mulai dari satu sambungan route. Pada `backend/routes/actuators.php`, temukan baris berikut yang menghubungkan POST dengan method `register()`. Ini cuplikan berkas yang tersedia; jangan menambah route kedua dengan alamat sama.

```php
Route::post('/aktuator', [ActuatorController::class, 'register']);
```

Provider menambahkan awalan `/api/v1`. Periksa `ActuatorServiceProvider` dan daftar pada `bootstrap/providers.php`; menulis file route saja belum mendaftarkannya. Di controller, `register()` memvalidasi identitas, membuat perangkat bila belum ada, lalu mencari atau membuat aktuator. Pendaftaran baru menghasilkan HTTP201; pendaftaran ulang identitas yang sama menghasilkan HTTP200. Method lain dipelajari setelah pendaftaran pertama lulus.

Berikutnya, baca awal fungsi `value()` pada controller. Satu fungsi ini menentukan rentang berdasarkan jenis output sebelum perintah atau laporan disimpan:

```php
$value = $request->input('value');
$max = $actuator->kind === 'led' ? 1 : 180;
```

Baris berikutnya memeriksa `is_int($value)` dan batas bawah/atas. Karena itu, string `"90"` dan angka 181 sama-sama ditolak untuk servo. Validasi berlangsung sebelum transaksi penyimpanan; mahasiswa akan membuktikan tidak adanya baris tambahan pada langkah 12.

Baca `command()`: setelah aktuator dikunci untuk transaksi, perintah kedaluwarsa diperbarui dan pending lama diganti. Baris ini hanya mengubah target operator:

```php
$row->update(['requested_value' => $value]);
```

Sesudahnya `ActuatorCommand::create()` menyimpan satu perintah dengan `expires_at`. Nilai `reported_value` belum disentuh. Baru pada `acknowledge()`, setelah pemeriksaan ID, sesi, urutan, dan nilai, status perintah serta laporan diperbarui:

```php
$command->update(['status' => 'applied', 'acknowledged_at' => now()]);
$row->update(['reported_value' => $value, 'reported_at' => now(),
    'report_sequence' => $data['sequence']]);
```

Panggilan `ActuatorStateEvent::create()` pada baris berikutnya menambah riwayat. Ketiga perubahan berada di dalam `DB::transaction()`: jika satu gagal, seluruh perubahan transaksi dibatalkan. Jangan menyalin cuplikan di atas sebagai controller baru. Setelah memahami bagian yang berubah, gunakan berkas lengkap bawaan untuk percobaan berikut dan cocokkan respons dengan SQL.

## 3. Daftarkan satu LED dahulu

Pastikan simulator belum berjalan. Baca kembali `client_python/http_json.py` yang dipakai pada latihan MySQL. Fungsi `minta(metode, path, payload=None)` membentuk Request, menangani HTTPError/koneksi, menampilkan status dan JSON, lalu mengembalikan pasangan status/data. Pada skrip pendaftaran berikut, dictionary adalah payload yang akan diubah menjadi JSON oleh fungsi itu. Dari akar lab di terminal B, jalankan `python client_python/06_daftar_led.py`:

```python
from http_json import minta
from konfigurasi import ID_AKTUATOR

status, data = minta("POST", "/api/v1/aktuator",
    {"device_id": ID_AKTUATOR, "name": "lampu", "kind": "led"})
if status not in (200, 201):
    raise SystemExit(1)
```

Skrip menampilkan HTTP 201 beserta JSON yang memuat ID numerik. Jalankan skrip yang sama sekali lagi: respons HTTP200 memakai ID yang sama, sehingga tidak membuat output rangkap. Pendaftaran tidak memerlukan satu pun pembacaan sensor. Laravel membuat baris `devices` jika nama perangkat belum ada.

Pertahankan tiga identitas: `device_id` menunjuk ESP32, `name` menunjuk satu output pada ESP32 itu, dan `id` numerik dipakai pada URL API aktuator. Mengganti jenis pada identitas yang sama ditolak HTTP409.

## 4. Tambahkan servo sebagai output kedua

Dari akar lab, jalankan `python client_python/07_daftar_servo.py`. Perubahannya hanya nama/jenis output pada POST, lalu GET daftar. `urlencode` membentuk parameter `device_id` dari konfigurasi.

```python
from urllib.parse import urlencode
from http_json import minta
from konfigurasi import ID_AKTUATOR

status, data = minta("POST", "/api/v1/aktuator",
    {"device_id": ID_AKTUATOR, "name": "pintu", "kind": "servo"})
if status not in (200, 201):
    raise SystemExit(1)
parameter = urlencode({"device_id": ID_AKTUATOR})
status, daftar = minta("GET", "/api/v1/aktuator?" + parameter)
if status != 200:
    raise SystemExit(1)
```

Ada dua baris dengan nama `lampu` dan `pintu`, masing-masing mempunyai ID berbeda. Nilai target/laporan masih kosong jika baru pertama kali didaftarkan. Buka `/aktuator` dan pilih kedua output secara bergantian. Jangan menyalin ID angka dari screenshot; gunakan hasil pendaftaran Anda.

## 5. Simpan target saat ESP32 belum berjalan

Baca `client_python/aktuator.py` terlebih dahulu. Fungsi `cari_id(nama)` meminta daftar milik `ID_AKTUATOR`, menelusuri setiap baris, lalu mengembalikan ID output yang namanya cocok. Jika belum terdaftar, skrip berhenti dengan petunjuk pendaftaran; ID tidak ditebak dan tidak disimpan dalam variabel sesi terminal.

```python
from urllib.parse import urlencode
from http_json import minta
from konfigurasi import ID_AKTUATOR


def cari_id(nama):
    parameter = urlencode({"device_id": ID_AKTUATOR})
    status, daftar = minta("GET", "/api/v1/aktuator?" + parameter)
    if status != 200:
        raise SystemExit("Daftar gagal dibaca; periksa route aktuator.")
    for baris in daftar:
        if baris["name"] == nama:
            return baris["id"]
    raise SystemExit("Daftarkan " + nama + " dahulu dengan skrip 06 atau 07.")
```

Skrip berikut memanggil fungsi itu untuk `lampu`. Jalankan `python client_python/08_target_led.py` dari akar lab; `NILAI = 1` berarti nyala, sedangkan `0` berarti mati.

```python
from aktuator import cari_id
from http_json import minta

NILAI = 1
id_led = cari_id("lampu")
path = "/api/v1/aktuator/" + str(id_led)
status, perintah = minta("POST", path + "/perintah", {"value": NILAI})
if status != 202:
    raise SystemExit(1)
status, riwayat = minta("GET", path + "/riwayat")
if status != 200:
    raise SystemExit(1)
```

Respons HTTP202 berarti permintaan diterima dan disimpan, dengan status `pending`. Target LED menjadi 1. Laporan firmware tetap belum ada jika ESP32 belum pernah melapor. Halaman `/aktuator` memperlihatkan perbedaan ini. Mengirim target bukan bukti LED telah menyala.

Kontrak baru memakai `value` bilangan bulat: LED hanya 0 atau 1; servo 0 sampai 180. Kendali LED pada dashboard sensor lama memakai `led:true/false` dan URL `/perangkat/{device_id}`. Kedua latihan memiliki kontrak berbeda; jangan menukar body atau URL-nya.

## 6. Buktikan masa berlaku 30 detik

Biarkan ESP32 berhenti. Tunggu lebih dari 30 detik sejak perintah dibuat, kemudian jalankan `python client_python/09_baca_aktuator.py` dari akar lab. Perulangan luar memilih lampu/pintu; perulangan dalam meminta perintah dan riwayat masing-masing:

```python
from aktuator import cari_id
from http_json import minta

for nama in ("lampu", "pintu"):
    path = "/api/v1/aktuator/" + str(cari_id(nama))
    for akhir in ("/perintah", "/riwayat"):
        status, data = minta("GET", path + akhir)
        if status != 200:
            raise SystemExit(1)
```

`command` bernilai `null` dan perintah lama berstatus `expired`. Target terakhir tetap 1, tetapi tidak otomatis dijalankan kembali. Pada API aktuator, GET perintah/riwayat juga memperbarui status perintah yang kedaluwarsa. Karena tidak ada penjadwal latar pada lab, jalankan GET ini dahulu sebelum membandingkan kolom `status` melalui SQL. GET sensor pada latihan sebelumnya hanya membaca data sensor.

## 7. Uji output lokal sebelum memakai REST

Pada terminal PlatformIO di jendela `esp32_aktuator`:

```powershell
Copy-Item versi/01_gpio.cpp src/main.cpp -Force
pio run
```

Jalankan **Wokwi: Start Simulator** dari Command Palette. LED berubah dan servo bergantian ke 0, 90, lalu 180 tiap dua detik. Serial menulis `Uji lokal`. Tahap ini belum terhubung ke Laravel. Jika gerakan tidak terlihat, periksa diagram dan hasil build sebelum melanjutkan ke jaringan.

Buka `versi/01_gpio.cpp`. Siapkan output pada `setup()`:

```cpp
pinMode(23, OUTPUT);
digitalWrite(23, LOW);
ledcSetup(0, 50, 16);
ledcAttachPin(18, 0);
```

GPIO23 mengendalikan LED. Servo memakai kanal PWM 0 pada GPIO18, frekuensi 50 Hz atau periode 20.000 mikrodetik, dengan resolusi 16 bit. Bagian fungsi `sudutServo()` mengubah sudut menjadi pulsa:

```cpp
uint32_t pulsaUs = map(sudut, 0, 180, 500, 2500);
ledcWrite(0, (pulsaUs * 65535UL + 10000UL) / 20000UL);
```

Pada contoh ini, 0/90/180 dipetakan ke 500/1500/2500 mikrodetik. Penyebut 20.000 berasal dari periode 50 Hz; 65.535 adalah nilai duty maksimum 16 bit. Penambahan 10.000 membulatkan hasil pembagian. Nilai yang digunakan sesuai platform terkunci `espressif32@6.12.0` dengan Arduino ESP32 2.0.17. API LEDC pada Arduino ESP32 versi lain dapat berbeda. Pertahankan versi `platformio.ini` saat mengikuti langkah ini.

## 8. Kenali data dan fungsi klien, satu per satu

Hentikan simulator. Buka `include/config.h`: pertahankan `DEVICE_ID` sebagai `esp32-aktuator-01` agar sesuai dua pendaftaran tadi. `API_BASE` untuk firmware Wokwi adalah `http://host.wokwi.internal:8000`. Browser laptop tetap memakai `http://127.0.0.1:8000`. Nama host Wokwi mengarah ke laptop melalui integrasi jaringan Wokwi for VS Code yang dipakai pada lab. Wokwi web tidak otomatis dapat mencapai API localhost laptop.

File `include/actuator_client.h` menyimpan fungsi yang digunakan ulang oleh versi 02 dan 03. File sudah tersedia; jangan menempelkannya seluruhnya ke `main.cpp`. Untuk mempelajari pembuatannya, ikuti urutan baca berikut. Selesaikan tujuan pada tiap baris sebelum mengaktifkan versi 02.

| Urutan baca | Bagian | Satu hal yang ditambahkan |
|---|---|---|
| 1 | `struct Aktuator` | Menyimpan nama/jenis, ID dari server, nilai output, nomor urut, penanda siap, dan body konfirmasi yang belum terkirim |
| 2 | `api()` | Membuka HTTP, memasang header JSON, memilih GET/POST, membaca kode respons, lalu menutup koneksi |
| 3 | `mulaiWifi()` / `wifiSiap()` | Membuat `bootId` untuk sesi saat ini, terhubung ke Wi-Fi, dan mencoba sambungan ulang |
| 4 | `laporan()` | Membentuk JSON nilai, sesi boot, nomor urut dan alasan; setiap laporan mendapat urutan baru |
| 5 | `daftarkan()` | POST identitas, membaca ID numerik, kemudian POST laporan boot; aktuator siap hanya setelah laporan diterima |
| 6 | `periksa()` | GET perintah, periksa tipe/rentang, panggil fungsi output, lalu siapkan konfirmasi |
| 7 | `kirimKonfirmasi()` | POST konfirmasi dan mengulang body yang sama bila sambungan gagal |
| 8 | `heartbeat()` | Mengirim laporan berkala tanpa mengubah output |

`boot_id` adalah identitas sesi sejak ESP32 dinyalakan, bukan password. `sequence` adalah nomor urut laporan dalam sesi itu. API menolak laporan lama yang dapat menimpa keadaan baru. Selama `boot_id` masih sama, konfirmasi perintah yang sudah diterima boleh dikirim ulang dengan ID yang sama: hasil tetap `applied`, tanpa event kedua atau pengembalian nilai ke keadaan lama. Konfirmasi dari sesi sebelum restart ditolak HTTP409.

Pada parameter `Aktuator& a`, tanda `&` berarti fungsi bekerja pada objek yang sama, sehingga ID dan urutan baru tetap tersimpan setelah fungsi selesai. Parameter `void (*terapkan)(int)` menerima nama fungsi output yang memakai satu bilangan dan tidak mengembalikan nilai. Pemanggilan `periksa(lampu, terapkanLed)` berarti periksa perintah untuk objek lampu, kemudian jalankan `terapkanLed(nilai)` saat nilai sudah valid. Versi berikutnya memakai proses HTTP yang sama dengan fungsi `terapkanServo` sebagai penggantinya.

Tiga cuplikan berikut sudah ada pada berkas; baca tanpa menyisipkannya kembali. Pada `versi/02_led_rest.cpp`, bentuk objek yang memegang keadaan lampu:

```cpp
Aktuator lampu{"lampu", "led"};
```

Saat `daftarkan(lampu)` berjalan, parameter `a` merujuk objek lampu tadi. Baris pada `include/actuator_client.h` ini menyimpan ID server ke objek tersebut:

```cpp
a.id = doc["id"];
```

Kembali ke `loop()` versi 02, baca pemanggilan yang menyerahkan fungsi output. Perintah HTTP tidak langsung menyalakan LED sampai `periksa()` memperoleh nilai yang valid:

```cpp
periksa(lampu, terapkanLed);
```

Perhatikan batas waktu pada `api()`: koneksi dua detik dan pembacaan tiga detik. Setelah koneksi gagal, loop dapat mencoba lagi; program tidak menunggu Wi-Fi selamanya di `setup()`. Konfirmasi harus menyusul perubahan output. Jangan memindahkan POST konfirmasi ke sebelum `digitalWrite()` atau `ledcWrite()`.

## 9. Hubungkan LED dahulu ke REST

Di jendela PlatformIO, pada folder `esp32_aktuator`:

```powershell
Copy-Item versi/02_led_rest.cpp src/main.cpp -Force
pio run
```

Jalankan simulator. Baca berkas versi 02: `setup()` menetapkan LED mati sebelum Wi-Fi. `loop()` memanggil `periksa(lampu, terapkanLed)` setiap satu detik dan `heartbeat(lampu)` setiap sepuluh detik. `terapkanLed()` menerima satu nilai dan memanggil `digitalWrite()`; data HTTP tetap ditangani fungsi klien yang telah dibaca pada langkah 8.

Serial menampilkan `Sesi ...`, lalu `BOOT lampu id=... nilai=0 -> 200`. ID harus sama dengan pendaftaran `lampu` tadi. Buka `/aktuator`, pilih LED, dan pastikan laporan 0. Servo belum ditangani versi ini. `requested_value` lama dapat tetap 1; ini memang memperlihatkan perbedaan target dan keadaan saat boot.

Jika belum ada baris BOOT, periksa Wi-Fi, terminal Laravel, URL `config.h`, dan `GET /api/v1/health` di laptop. HTTP500 perlu diperiksa pada log Laravel; HTTP404 biasanya menunjukkan route atau ID yang salah. Daftar dapat berisi hasil pendaftaran manual langkah 3 dan 4. Pastikan firmware mencetak BOOT dengan status 200 dan waktu laporan diperbarui; keberadaan nama pada daftar saja belum membuktikan koneksi firmware.

Jika restart Wokwi terus menampilkan sesi Serial lama atau berhenti pada Connecting to WiFi, hentikan simulasi dan tutup tab Wokwi. Jalankan **Developer: Reload Window** dari Command Palette, lalu **Wokwi: Start Simulator**. Tunggu BOOT 200 yang baru sebelum menguji perintah. Langkah pemulihan ini memuat ulang ekstensi, tidak menghapus database.

## 10. Telusuri satu perintah LED sampai ke MySQL

Pada `/aktuator`, pilih `esp32-aktuator-01 / lampu`, tekan **Nyalakan LED**. Tunggu `applied`; jangan langsung menekan tombol lain. Urutannya:

1. Browser POST `{"value":1}`; Laravel menyimpan satu perintah dan mengembalikan ID serta HTTP202.
2. Firmware GET perintah tersebut pada pemeriksaan berikutnya.
3. Firmware memeriksa nilai, menjalankan `digitalWrite()`, lalu membaca GPIO23 menggunakan `digitalRead()`.
4. Firmware POST `command_id`, `value`, `boot_id`, dan `sequence` ke `/konfirmasi`.
5. Laravel mengubah status perintah menjadi `applied`, memperbarui laporan terakhir, dan menambah satu event dalam satu transaksi MySQL.

Serial menulis `APPLY lampu command=... nilai=1` dan `ACK lampu nilai=1 -> 200`. Cocokkan ID perintah dengan baris dashboard dan SQL pada langkah 13. Ulangi **Matikan LED** dan cocokkan ID baru. Perintah pending yang diganti perintah lebih baru menjadi `superseded`; konfirmasi lama tidak boleh menimpanya.

## 11. Tambahkan servo setelah LED lulus

Hentikan simulator. Pada terminal PlatformIO:

```powershell
Copy-Item versi/03_led_servo_rest.cpp src/main.cpp -Force
pio run
```

Versi 03 adalah program lengkap dan merupakan isi awal `src/main.cpp` pada paket. Bandingkan dengan versi 02. Tambahannya adalah objek `pintu`, fungsi `terapkanServo()`, inisialisasi PWM pada `setup()`, serta panggilan `periksa()` dan `heartbeat()` kedua pada `loop()`. Fungsi HTTP tetap sama. Rangkaian tidak berubah dari tahap lokal.

Jalankan simulator dan tunggu dua laporan BOOT. Pilih `pintu` pada `/aktuator`. Kirim sudut **0**, tunggu `applied`; ulangi **90**, lalu **180**. Serial mencatat sudut, pulsa, duty, ID perintah, dan hasil konfirmasi. Cocokkan gerakan servo di Wokwi dengan laporan dashboard. LED tetap dapat dikendalikan secara terpisah.

Jangan menyebut angka dashboard sebagai posisi mekanis yang diukur. Firmware mengonfirmasi nilai yang sudah diberikan kepada PWM. Pada perangkat fisik, motor dapat macet atau kehilangan suplai meskipun firmware telah mengirim PWM; pembuktian posisi memerlukan umpan balik tambahan.

Untuk mengirim servo melalui Python, baca `client_python/10_servo.py`. Fungsi pencarian ID dan fungsi HTTP sudah dipakai pada langkah LED; tambahan di sini hanya `SUDUT`. Dari akar lab, jalankan `python client_python/10_servo.py`, tunggu `applied`, lalu ubah 90 menjadi 0 atau 180, simpan, dan jalankan ulang satu nilai pada satu waktu.

```python
from aktuator import cari_id
from http_json import minta

SUDUT = 90
path = "/api/v1/aktuator/" + str(cari_id("pintu")) + "/perintah"
status, perintah = minta("POST", path, {"value": SUDUT})
if status != 202:
    raise SystemExit(1)
```

## 12. Periksa validasi dan laporan berkala

Sebelum uji, jalankan `python client_python/09_baca_aktuator.py` dari akar lab. Catat ID perintah terakhir dan daftar ID pada `commands` milik pintu. Selama percobaan ini, jangan mengirim perintah lain dari dashboard. Lalu jalankan `python client_python/11_uji_servo_salah.py`. Skrip sengaja mengirim nilai 181, lalu memeriksa bahwa statusnya 422:

```python
from aktuator import cari_id
from http_json import minta

path = "/api/v1/aktuator/" + str(cari_id("pintu")) + "/perintah"
status, hasil = minta("POST", path, {"value": 181})
if status != 422:
    raise SystemExit("Gagal: nilai 181 seharusnya ditolak HTTP 422.")
print("Sesuai: nilai di luar rentang ditolak.")
```

Skrip menampilkan HTTP 422 dengan pesan rentang yang valid, lalu pesan bahwa penolakan sesuai harapan. Kode keluar 0 berarti pengujian penolakan lulus; itu tidak berarti perintah 181 diterapkan. Jalankan kembali skrip 09 dan cocokkan daftar ID: tidak boleh ada ID perintah baru akibat nilai 181. Pemeriksaan jumlah baris melalui SQL tersedia pada langkah 13. LED dengan nilai 2 juga ditolak. Angka harus berupa bilangan bulat JSON: gunakan `90`, bukan `"90"`, `90.5`, atau `true`.

Biarkan simulator berjalan tanpa perintah baru selama lebih dari sepuluh detik. `reported_at` diperbarui oleh heartbeat, yaitu laporan berkala. Jika nilai tetap sama, jumlah event tidak bertambah. Waktu event terakhir dapat lebih lama daripada waktu laporan terakhir. Halaman menandai laporan yang berumur lebih dari 20 detik; waktu ini merupakan indikator latihan, bukan jaminan perangkat sehat.

## 13. Cocokkan tiga tabel lewat SQL

Jalankan kueri berikut melalui klien MySQL pada database lab yang sama dengan `.env`. Jangan menempelkan SQL ke C++ atau terminal shell biasa. Salinan siap pakai tersedia pada `tests/inspect_actuators.sql`.

```sql
SELECT id, device_id, name, kind,
       requested_value, reported_value, boot_id, reported_at
FROM actuators
WHERE device_id = 'esp32-aktuator-01';
```

Untuk setiap ID, lihat target dan laporan terakhir. Lalu telusuri ID perintah:

```sql
SELECT c.id, a.name, c.value, c.status, c.acknowledged_at
FROM actuator_commands c
JOIN actuators a ON a.id = c.actuator_id
WHERE a.device_id = 'esp32-aktuator-01'
ORDER BY c.id DESC;
```

Terakhir, periksa laporan yang merujuk perintah tersebut:

```sql
SELECT e.id, a.name, e.command_id, e.value,
       e.reason, e.boot_id, e.sequence, e.created_at
FROM actuator_state_events e
JOIN actuators a ON a.id = e.actuator_id
WHERE a.device_id = 'esp32-aktuator-01'
ORDER BY e.id DESC;
```

Satu konfirmasi perintah yang berhasil menghasilkan satu event `reason=command` dengan `command_id` yang sama. Laporan boot tidak mempunyai ID perintah. Timestamp database disimpan dalam UTC; dashboard menampilkannya dalam WIB. Data ini adalah catatan penerimaan server, bukan pengukuran waktu motor bergerak.

## 14. Mulai ulang ESP32, lalu pulihkan dengan perintah baru

Nyalakan LED dan kirim servo 90; tunggu keduanya `applied`. Catat target, laporan dan `boot_id`. Untuk mengulang sesi jaringan pada workflow yang diuji, hentikan simulasi, tutup tab Wokwi, jalankan **Developer: Reload Window**, kemudian **Wokwi: Start Simulator**. Tunggu dua BOOT 200 yang baru. Setelah boot selesai, output awal menjadi 0, `boot_id` berubah, dan ada event boot baru. Target lama tetap tersimpan. Perintah lama yang sudah `applied` tidak dijalankan ulang. Jika memakai tombol Restart pada Wokwi dan laporan baru tidak masuk, gunakan urutan pemulihan ini; jangan menganggap tampilan bergerak sebagai bukti API sudah terhubung.

Kirim perintah baru untuk menerapkan target kembali. Uji tambahan: hentikan/pause simulator, simpan perintah baru, lalu ulangi sesi menggunakan urutan di atas. Jika BOOT 200 diterima API sebelum `expires_at`, pending lama menjadi `superseded`. Jika laporan boot tiba setelah batas itu, status `expired` adalah hasil yang sesuai. Perintah sebelum restart tidak dijalankan kembali tanpa perintah baru dari operator.

## 15. Buktikan data bertahan setelah Laravel dimulai ulang

Catat beberapa ID perintah/event yang sudah tersimpan. Hentikan server di terminal A dengan Ctrl+C. Terminal itu masih berada di folder `backend`; ketik `php artisan serve --host=127.0.0.1 --port=8000` tanpa mengulangi `cd backend`. Jangan menghapus database. Tekan **Perbarui data** pada halaman. Perintah dan event lama harus tetap ada karena tersimpan pada MySQL, bukan hanya pada memori browser atau PHP.

Kembalikan LED ke mati dan servo ke 0 dengan perintah baru. Simpan bukti yang cukup untuk menjelaskan satu alur lengkap, bukan hanya screenshot antarmuka.

## 16. Lembar kerja dan arah proyek

| Bukti yang diserahkan | Yang harus dapat dijelaskan |
|---|---|
| Dua hasil pendaftaran dan SELECT `actuators` | Perbedaan ID perangkat, nama output, dan ID numerik |
| Target pending saat simulator berhenti | Alasan target belum sama dengan laporan |
| Satu perintah expired | Batas berlaku dan perlunya GET sebelum memeriksa status SQL |
| LED nyala/mati dan servo 0/90/180 | Satu ID dapat ditelusuri dari browser ke Serial dan MySQL |
| Nilai 181 ditolak | HTTP422 tidak membuat perintah baru |
| Laporan sebelum/sesudah restart | Target tetap ada, output awal dan sesi berubah |
| ID lama setelah server dimulai ulang | Bukti penyimpanan MySQL |

Untuk proyek akhir, pola LED dapat menjadi simulasi output biner seperti pompa atau kipas; servo dapat menjadi contoh bukaan ventilasi. Simulasi tersebut tidak menguji pompa/kipas fisik. Mahasiswa perlu menetapkan rentang, kondisi awal, masa berlaku perintah, konsekuensi kegagalan koneksi, serta jenis umpan balik sebelum menambah output lain. Otomasi berdasarkan sensor merupakan tugas lanjutan: jelaskan aturan dan sumber keputusan operator/otomatis agar keduanya tidak saling menimpa.

## Rujukan dan pemeriksaan kode

Pin dan rentang servo mengikuti [referensi Wokwi servo](https://docs.wokwi.com/parts/wokwi-servo). Fungsi PWM memakai [header resmi Arduino ESP32 2.0.17](https://github.com/espressif/arduino-esp32/blob/2.0.17/cores/esp32/esp32-hal-ledc.h). Route tambahan didaftarkan melalui [service provider Laravel 12](https://laravel.com/docs/12.x/providers). Versi paket dan cakupan pengujian dicatat pada `bukti/aktuator_verifikasi.json`; hasil pengujian tidak menyatakan efektivitas pembelajaran atau hasil uji perangkat fisik.

Untuk pengajar, dari `backend` jalankan `php vendor/bin/phpunit tests/Actuators` pada database pengujian yang sudah disiapkan. Suite sensor lama tetap dijalankan dengan `php vendor/bin/phpunit`. Jangan mengarahkan `.env.testing` ke database bukti kelas.

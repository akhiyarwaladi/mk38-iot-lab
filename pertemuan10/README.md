# Praktik MQTT pertemuan 10

Gunakan Visual Studio Code, PlatformIO, Wokwi, dan Node.js 24 LTS.
Rangkaian: ESP32, DHT22 GPIO 15, serta LED GPIO 23 melalui resistor 220 ohm.
`diagram.json` sudah tersedia pada ketiga proyek ESP32.

## Urutan

1. Buka `01_publish`, ubah `include/config.h`, build, dan jalankan Wokwi.
2. Pantau topic `/pesan` dengan MQTT Explorer atau client terminal di bawah.
3. Hentikan simulator. Buka `02_sensor`; ubah konfigurasi ke topic root yang sama.
4. Build, jalankan, lalu cocokkan penggeser DHT22 dengan JSON `/sensor`.
5. Hentikan simulator. Buka `03_kendali` dan ulangi konfigurasi serta build.
6. Kirim teks `on` atau `off` ke `/led/set`, QoS 1, retain tidak aktif.
7. Periksa LED, keluaran pin pada Serial Monitor, dan pesan `/led/state`.

Contoh topic root: `unja/mk38/p10/kelompok-01-nim-anda`. Ganti bagian
identitas; satu topic root dipakai satu kelompok. Hentikan proyek tahap
sebelumnya agar koneksi dengan ID yang sama tidak saling menggantikan.

## Node-RED dan client terminal

Buka terminal pada folder `node_red`, samakan `topicRoot` dalam
`config.json` dengan ESP32, lalu jalankan:

```powershell
node --version
npm.cmd ci
npm.cmd start
```

Biarkan terminal tersebut tetap berjalan. Buka:

- Editor: `http://localhost:1880/`
- dashboard: `http://localhost:1880/dashboard/ruangan`
- Riwayat JSON: `http://localhost:1880/api/riwayat`

Pada terminal kedua, dari folder `node_red`:

```powershell
node mqtt_cli.js watch
```

Pada terminal ketiga:

```powershell
node mqtt_cli.js send on
node mqtt_cli.js send off
node mqtt_cli.js send salah
```

Hentikan pemantau dan Node-RED dengan Ctrl+C. Setelah ESP32 dihentikan,
bersihkan retained state kelompok sendiri:

```powershell
node mqtt_cli.js clear
```

## Mengubah alur

`npm.cmd start` menyusun ulang `flow.runtime.json` dari `flow.template.json`
dan konfigurasi. Perubahan melalui editor Node-RED perlu diekspor sebelum
Node-RED dimulai ulang. Untuk menyimpan perubahan sebagai sumber paket,
edit `flow.template.json` atau berkas pada `functions/`, sesuai bagian
yang diubah. Simpan hasil ekspor tugas dalam berkas JSON terpisah.

SQLite membuat tabel otomatis pada `data/sensor.sqlite`. Jalankan proyek
dari folder yang sama agar riwayat tetap terbaca. Grafik dashboard menyimpan
sesi tampilan; periksa API untuk membuktikan penyimpanan setelah restart.
Saat baru mulai dan belum menerima sensor, angka awal widget belum
merupakan bacaan sensor baru.

## Bila ekstensi Wokwi belum aktif

Build tetap dilakukan dengan PlatformIO. Pada Wokwi web, masukkan
`diagram.json`, tekan F1 di editor, pilih Upload Firmware and Start Simulation,
kemudian pilih `.pio/build/esp32dev/firmware.bin` dari proyek yang sama.
Pengujian modul memakai cara ini untuk mengeksekusi hasil kompilasi lokal.

## Pembelajaran bertahap

ESP32: 01_publish → 02_sensor → 03_kendali. Node-RED: tahap 1 → 2 → 3 → 4. Ekspor perubahan editor sebelum mengganti tahap.

Mulai dari [panduan tahapan](TAHAPAN.md). Kode lengkap dipakai setelah bukti tiap tahap diperiksa; lihat PDF untuk penjelasan konstruksi dan posisi setiap tambahan.

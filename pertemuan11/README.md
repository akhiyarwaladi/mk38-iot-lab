# Praktik pertemuan 11

Gunakan Visual Studio Code, PlatformIO, Wokwi, dan Node.js 24 LTS.
Mulai dari folder `esp32_cloud`, kemudian jalankan `node_red`.

## Firmware

1. Ubah `TOPIC_ROOT` dalam `esp32_cloud/include/config.h`.
2. Pertahankan `MODE_BACA_PUBLIK=true` untuk diagnosis HTTPS tanpa akun.
3. Jalankan PlatformIO: Build, lalu Wokwi: Start Simulator.
4. Cocokkan DHT22 dengan payload MQTT. Baca status HTTPS channel publik.

Suhu/kelembapan dibaca dari DHT22 GPIO 15. LED berada pada GPIO 23
melalui resistor 220 ohm. Rangkaian sudah ada dalam `diagram.json`.

`src/main.cpp` mengurus WiFi, MQTT, sensor, dan jadwal REST.
`src/cloud.cpp` mengirim HTTPS serta memeriksa response.
`src/cloud_worker.cpp` menjalankan HTTPS melalui antrean FreeRTOS.
`include/cloud.h` mendeklarasikan hasil dan fungsi pengiriman.
File CA memuat sertifikat publik; verifikasi TLS tetap aktif.

Untuk ThingSpeak, buat channel dengan Field 1 Suhu, Field 2 Kelembapan,
dan Field 3 LED. Salin `include/secrets.example.h` sebagai
`include/secrets.h`, isi Write API Key sendiri, lalu ubah MODE_BACA_PUBLIK ke
false dan build ulang. Jangan mengumpulkan key tersebut.

## Node-RED

Buka terminal pada folder `node_red`, samakan `topicRoot` pada
`config.json` dengan firmware, lalu jalankan:

```powershell
npm.cmd ci
npm.cmd start
```

Pada Linux/macOS, gunakan `npm`. Buka:

- Editor: `http://localhost:1880/`
- Dashboard: `http://localhost:1880/dashboard/ruangan`
- Riwayat SQLite: `http://localhost:1880/api/riwayat`

Pada terminal kedua di folder yang sama:

```powershell
node mqtt_cli.js watch
```

Pada terminal ketiga:

```powershell
node mqtt_cli.js send on
node mqtt_cli.js send off
node mqtt_cli.js send salah
```

Saat worker HTTPS berjalan, main loop tetap melayani MQTT. Cocokkan
keadaan LED dengan state dari ESP32. Dashboard menunggu data pertama
sebelum menampilkan angka sensor.

Perubahan flow melalui editor perlu diekspor sebelum restart, karena
`npm.cmd start` membuat ulang flow.runtime.json dari template. SQLite
menyimpan riwayat di `data/sensor.sqlite`, sedangkan grafik adalah tampilan
sesi dashboard.

## Mode dan bukti

HTTP 200 dengan read_ok=true membuktikan pembacaan channel publik 9.
Penyimpanan cloud memerlukan mode ThingSpeak, entry ID positif, dan data
yang cocok pada channel kelompok. Baca publik belum melengkapi bagian cloud
storage pada Tugas 3.

Setelah ESP32 dihentikan, jalankan `node mqtt_cli.js clear` untuk
membersihkan retained state kelompok sendiri. Hentikan layanan dengan Ctrl+C.

Gunakan `laporan_tugas3.md` dan `proposal_proyek.md` untuk penyerahan.

## Channel demonstrasi

Channel demonstrasi dosen memiliki ID 3560582. Konfigurasi Write API Key tersedia pada `esp32_cloud/include/secrets.demo.h`, sesuai permintaan pengguna. Dari terminal PlatformIO di folder `esp32_cloud`, salin `include/secrets.demo.h` menjadi `include/secrets.h`, lalu build. Untuk pertemuan 11, ubah `MODE_BACA_PUBLIK=false` sebelum build dan samakan topic root ESP32/Node-RED. Jalankan satu pengirim pada channel demonstrasi; kelompok menggunakan channel masing-masing. Read API Key tidak disertakan.

Bukti penulisan dari ESP32 virtual, pembacaan ulang ThingSpeak, serta kendali tersimpan pada folder bukti di ZIP sumber. Lihat VERIFIKASI.md dan PDF untuk urutan yang lengkap.

## Pembelajaran bertahap

01_https.cpp → 02_parse.cpp → 03_task.cpp → 04_worker.cpp → 99_lengkap.cpp. Lakukan versi kecil sebelum kelas, integrasi dan demo saat sesi.

Mulai dari [panduan tahapan](TAHAPAN.md). Kode lengkap dipakai setelah bukti tiap tahap diperiksa; lihat PDF untuk penjelasan konstruksi dan posisi setiap tambahan.

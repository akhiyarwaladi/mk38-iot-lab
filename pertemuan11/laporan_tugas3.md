# Laporan Tugas 3 MK38

Nama kelompok dan anggota:
Tanggal pengujian:
Topic root:
Platform cloud dan Channel ID (tanpa key):
Lokasi dashboard: lokal/cloud, tuliskan alamat yang digunakan tanpa key.

## 1. Jalur sistem

Tuliskan urutan sensor, ESP32, HTTPS, cloud storage, MQTT broker,
dashboard, dan control. Jelaskan fungsi tiap layanan.

## 2. Hasil sensor dan REST

| No. | Waktu | Suhu | Kelembapan | LED | Mode | HTTP | Entry ID cloud | Bukti pada channel |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |

Entry yang dibaca dari channel publik tidak dihitung sebagai pengiriman
sensor kelompok ke cloud storage. Tandai bagian yang
belum dapat diuji dan jelaskan penyebabnya.

## 3. MQTT dan control

| Topic | Publisher | Subscriber | QoS publish/subscribe | Retain | Payload |
|---|---|---|---|---|---|
| /sensor | | | | | |
| /led/set | | | | | |
| /led/state | | | | | |
| /cloud/status | | | | | |

| Perintah | Keadaan sebelum | Pin sesudah | State MQTT | Waktu/jeda | Bukti |
|---|---|---|---|---|---|
| on | | | | | |
| off | | | | | |
| salah | | | | | |

## 4. Gangguan dan pemulihan

Tuliskan satu kegagalan yang benar-benar diuji, hasilnya, tindakan
perbaikan, dan bukti sesudah pulih. Cocokkan waktu bila hasil datang terlambat.

## 5. Berkas dan kontribusi

Sertakan source tanpa secrets.h, platformio.ini, flow JSON, screenshot
dashboard dan channel, serta tabel pengamatan. Daftar kontribusi tiap anggota.

## 6. Penjelasan

Bedakan transport HTTPS, penyimpanan cloud, dashboard lokal, SQLite,
dan konfirmasi control. Jelaskan alasan memilih platform.

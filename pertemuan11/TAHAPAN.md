# Urutan latihan pertemuan 11

01_https.cpp → 02_parse.cpp → 03_task.cpp → 04_worker.cpp → 99_lengkap.cpp. Lakukan versi kecil sebelum kelas, integrasi dan demo saat sesi.

Baca bagian pengembangan kode bertahap pada PDF pertemuan ini sebelum menjalankan kode lengkap.

## Prasyarat dan berkas pembuka

Proyek MQTT pertemuan 10; Wi-Fi/NTP/CA; peta main.cpp, cloud.h, cloud.cpp, dan cloud_worker.cpp.

## Titik awal yang kecil

Versi 01_https.cpp mencetak respons GET mentah; belum ada MQTT, sensor, atau penulisan channel.

## Perubahan antarversi

HTTPS mentah, hasil respons dalam CloudResult, task tanpa jaringan, worker/antrean, kemudian integrasi MQTT lengkap.

## Cara menjalankan

Dari esp32_cloud, ganti hanya src/main.cpp melalui Copy-Item versi/<nama>.cpp src/main.cpp, lalu pio run dan unggah BIN baru.

## Bukti sebelum lanjut

Status HTTP dan isi respons, read_ok dan ID publik, keluaran TASK/MAIN, loop tetap berjalan ketika pekerjaan REST diantrekan, lalu MQTT dan LED.

## Hubungan ke versi lengkap dan batas

Enam langkah menjelaskan konstruksi worker. Peta memisahkan deklarasi header, implementasi, pemanggil, dan hasil; GET publik tetap berbeda dari POST sensor.

Simpan hasil setiap tahap. Perintah harus dijalankan dari folder yang disebut, bukan dari folder ZIP yang belum diekstrak. Pada proyek ESP32, versi CPP disimpan di luar src; satu main.cpp aktif pada setiap build. Simpan perubahan sendiri sebelum menyalin versi lain. Hentikan proses/simulasi versi sebelumnya sebelum mengganti tahap.

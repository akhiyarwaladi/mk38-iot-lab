# Urutan latihan pertemuan 9

03_cloud: 01_https.cpp → 02_payload.cpp → 99_lengkap.cpp. 04_server: 01_teks.cpp → 02_sensor.cpp → 99_lengkap.cpp.

Baca bagian pengembangan kode bertahap pada PDF pertemuan ini sebelum menjalankan kode lengkap.

## Prasyarat dan berkas pembuka

Wi-Fi dan DHT22 dari tahap 1/2; folder proyek yang berisi platformio.ini; CA dan penerusan port.

## Titik awal yang kecil

03_cloud/versi/01_https.cpp membaca respons publik tanpa akun; 04_server/versi/01_teks.cpp hanya melayani GET teks.

## Perubahan antarversi

GET HTTPS, payload sensor lokal, POST lengkap; server teks, JSON sensor, lalu POST LED dan HTML.

## Cara menjalankan

Dari folder proyek aktif, Copy-Item versi/<nama>.cpp src/main.cpp, pio run, lalu mulai simulasi BIN baru.

## Bukti sebelum lanjut

Status HTTP dan isi respons GET; dua masukan sensor; respons GET /; JSON /sensor; GPIO dan status HTTP setelah POST.

## Hubungan ke versi lengkap dan batas

99_lengkap.cpp cocok dengan src/main.cpp bawaan. Pembentukan payload dan rute dipetakan ke fungsi lengkap; penulisan cloud menunggu akun sendiri.

Simpan hasil setiap tahap. Perintah harus dijalankan dari folder yang disebut, bukan dari folder ZIP yang belum diekstrak. Pada proyek ESP32, versi CPP disimpan di luar src; satu main.cpp aktif pada setiap build. Simpan perubahan sendiri sebelum menyalin versi lain. Hentikan proses/simulasi versi sebelumnya sebelum mengganti tahap.

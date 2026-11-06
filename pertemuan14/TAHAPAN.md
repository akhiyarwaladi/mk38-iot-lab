# Urutan latihan pertemuan 14

Siapkan dua broker lab → 01_terima.py → 02_simpan.py → 03_kirim.py → gateway.py → uji putus/restart/pulih → Pi/service.

Baca bagian pengembangan kode bertahap pada PDF pertemuan ini sebelum menjalankan kode lengkap.

## Prasyarat dan berkas pembuka

Venv, paho, CA lokal, password environment; dua broker lab, dua port, dan dua CA; config.uji-lokal.json.

## Titik awal yang kecil

tahapan/01_terima.py menampilkan pesan saja; koneksi.py menyiapkan TLS dan config sebelum callback digunakan.

## Perubahan antarversi

Menerima pesan, validasi/INSERT offline, SELECT/publish/PUBACK/UPDATE, lalu loop gateway dan cabang kendali.

## Cara menjalankan

Perintah Windows, empat peran terminal, --config, --role cloud, dua broker, serta perintah Pi dipisahkan dan ditulis.

## Bukti sebelum lanjut

Pesan diterima; baris pending bertambah; input salah tidak INSERT; event_id cocok; pending pulih setelah tujuan hidup kembali.

## Hubungan ke versi lengkap dan batas

make_client/process/flush_one/run dipetakan ke tahap kecil. Database tahapan.sqlite dan gateway-uji.sqlite sengaja berbeda dan tidak dipindah otomatis.

Simpan hasil setiap tahap. Perintah harus dijalankan dari folder yang disebut, bukan dari folder ZIP yang belum diekstrak. Pada proyek ESP32, versi CPP disimpan di luar src; satu main.cpp aktif pada setiap build. Simpan perubahan sendiri sebelum menyalin versi lain. Hentikan proses/simulasi versi sebelumnya sebelum mengganti tahap.

# Urutan latihan pertemuan 12

Fritzing: komponen → catu/ground → data/pull-up → LED → schematic. CAD: 01_balok.scad → 02_rongga.scad → 03_usb.scad → enclosure.scad.

Baca bagian pengembangan kode bertahap pada PDF pertemuan ini sebelum menjalankan kode lengkap.

## Prasyarat dan berkas pembuka

Pin map pertemuan 11, varian komponen, ukuran dalam mm, serta perbedaan data ukur dan asumsi.

## Titik awal yang kecil

Fritzing dimulai dari komponen tanpa kabel; enclosure/tahapan/01_balok.scad hanya membuat balok luar.

## Perubahan antarversi

Satu net setiap tahap; balok, rongga, bukaan USB, lalu boss/lid/ventilasi pada model lengkap.

## Cara menjalankan

Buka satu SCAD setiap kali; F5, ukur dan putar, F6, lalu Export as STL ke nama berbeda. Padanan operasi Tinkercad disebutkan.

## Bukti sebelum lanjut

Kelima net cocok; dasar dan dinding tidak hilang; ukuran 110 x 80 x 35 mm tetap; bukaan menembus dinding.

## Hubungan ke versi lengkap dan batas

Module base, screw_positions, lid, union/difference, serta part dijelaskan hubungannya. Mesh valid belum membuktikan kecocokan hasil cetak.

Simpan hasil setiap tahap. Perintah harus dijalankan dari folder yang disebut, bukan dari folder ZIP yang belum diekstrak. Pada proyek ESP32, versi CPP disimpan di luar src; satu main.cpp aktif pada setiap build. Simpan perubahan sendiri sebelum menyalin versi lain. Hentikan proses/simulasi versi sebelumnya sebelum mengganti tahap.

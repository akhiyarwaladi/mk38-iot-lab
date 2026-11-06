# Praktik desain pertemuan 12

Gunakan PDF sebagai urutan workshop. Folder ini memuat contoh dan template
yang dapat diubah; tidak ada data anggota, harga, atau hasil ukur rekaan.

Jalankan `python cek_desain.py` dari folder ini. Python standar cukup untuk
membandingkan lima net pada `rangkaian/pinmap.csv`, `diagram.json`, dan
`acuan_logika.fzz`. Keluaran PASS hanya membuktikan konsistensi koneksi.

`acuan_logika.fzz` memakai simbol fungsional ESP32, DHT22, resistor, dan LED.
Nama DHT22 `SDA` mengikuti diagram Wokwi dan berarti DATA, bukan I2C.
Kedua view acuan tidak menunjukkan posisi pin fisik atau footprint PCB.
Buat breadboard view kelompok dengan komponen yang cocok sebelum merakit.

`enclosure/base.stl` berukuran 110 x 80 x 35 mm. `lid.stl` berukuran
110 x 80 x 5 mm dalam orientasi cetak: pelat 2 mm dan lip 3 mm.
Tutup dibalik pada rakitan, sehingga tinggi rakitan 37 mm. STL tidak
menyimpan satuan; pilih mm ketika impor dan periksa ukurannya.

Model tidak memuat board, breadboard, dudukan board, atau sensor fisik.
Bukaan USB, sensor, dan LED adalah ukuran latihan. Ukur varian komponen,
ubah sumber CAD, lalu periksa clearance dan hasil cetak. Empat boss sudut
merupakan pengikat tutup, bukan mounting hole ESP32.

Pada OpenSCAD, pilih `part="base"`, `part="lid"`, atau `part="assembly"`.
Gunakan F6 sebelum ekspor STL. Alternatif PowerShell dari folder `enclosure`:

```powershell
openscad.com -o base.stl -D 'part="base"' enclosure.scad
openscad.com -o lid.stl -D 'part="lid"' enclosure.scad
```

Model editable, STL base/lid, hasil ukuran, dua ekspor Fritzing, BOM, dan
progress report dikumpulkan bersama. Keluarkan API key serta folder build
dari paket yang diserahkan. Contoh firmware pertemuan 11 digunakan ulang
untuk uji komunikasi; Fritzing tidak menjalankan firmware ESP32.

## Pembelajaran bertahap

Fritzing: komponen → catu/ground → data/pull-up → LED → schematic. CAD: 01_balok.scad → 02_rongga.scad → 03_usb.scad → enclosure.scad.

Mulai dari [panduan tahapan](TAHAPAN.md). Kode lengkap dipakai setelah bukti tiap tahap diperiksa; lihat PDF untuk penjelasan konstruksi dan posisi setiap tambahan.

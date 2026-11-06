# Pemeriksaan antislop, bahasa, dan urutan belajar

Lingkup: dashboard Laravel, halaman latihan Blade, dan panduan lab pendamping. Mode antislop `during` mengikuti pilihan pengguna dalam percakapan. Arah desain ditetapkan pada `DESIGN.md` sebelum antarmuka dibuat. Pemeriksaan 6 November 2026 mengacu pada antislop, no-ai-slop, bahasa-inti, dan EYD. PASS di bawah berlaku untuk lingkup dan kondisi uji yang dicatat, bukan jaminan setiap perangkat atau kondisi jaringan.

## Delivery Gate: hard gate

- R-02 PASS: prosa dan teks antarmuka lab tidak memakai em dash; pemindaian sumber dilakukan sebelum pengemasan.
- R-03 PASS: browser pada lebar 320/390/768/1280 tidak mempunyai overflow halaman; kontrol utama minimal 44 px. Bukti: `browser_dashboard_checks.json` dan screenshot ponsel.
- R-17 PASS: pembacaan, ID, waktu, serta log perintah berasal dari MySQL; 244 kiriman pada snapshot SQL, tanpa statistik pemasaran.
- R-18 PASS: tidak ada testimoni, nama pelanggan, atau avatar fiktif.
- R-23 PASS: tidak membuat logo, foto, ilustrasi, atau navigasi pemasaran. Tangkapan layar adalah bukti pengujian yang diminta pengguna; navigasi hanya menuju latihan dan API yang dibuat dalam lab.
- R-24 PASS: Periksa API menuju health JSON; tautan tabel membuka Blade; tautan kembali membuka dashboard. Navigasi diperiksa di browser.
- R-25 PASS: 22 pasangan warna CSS lulus; teks minimum 5,74:1, border/fokus memenuhi 3:1. Hasil numerik: `dashboard_contrast.json`.
- R-26 PASS: pemilihan perangkat/jumlah, refresh, otomatis, tema, simpan ambang, nyala, mati, dan CSV mempunyai perilaku nyata. Perintah #3/#4 dikonfirmasi ESP32.
- R-27 PASS: keadaan memuat menyebut API, perangkat kosong menyebut menjalankan ESP32, dan API putus menyebut data sebelumnya serta cara mencoba lagi. Screenshot kosong/error tersedia.
- R-28 PASS: tidak ada bagian FAQ pengisi.
- R-32 PASS: kontrol memakai elemen native; Tab dari refresh menuju otomatis dan Space mengubah tema. Fokus tampak 3 px; skip link tersedia. Tidak ada modal yang memerlukan Escape.
- R-33 PASS: fitur ditulis langsung pada Blade, controller, route, CSS, JavaScript, dan firmware; script Python hanya membangun, membaca bukti, atau mengemas.
- R-34 PASS: kedua tema diperiksa pada desktop dan ponsel; teks, grafik, form, serta indikator memakai token tema yang sama.
- R-35 PASS: 12 uji/105 assertion, empat build firmware, uji Wokwi akhir, navigasi dan tindakan browser dicatat. Console pada muat ulang akhir tidak memuat error/warning.
- R-36 PASS: tidak mengklaim target satu detik atau kesiapan produksi. Waktu aktual 7,192/1,496 detik dan batas hasil ditulis pada verifikasi.
- R-37 PASS: pembaca, tugas layar, identitas seri modul, tipografi, komposisi, dan dials tertulis pada `DESIGN.md` sebelum pembuatan.
- R-38 PASS: angka dan riwayat merupakan data uji simulator; nilai kosong ditandai kosong. Ambang 30 °C disebut aturan latihan.
- R-39 PASS: `lang=id`, judul, main/header/footer, label terlihat, button/link native, cursor dan keadaan disabled/hover/focus tersedia. SVG berlabel dan tabel menyediakan nilai lengkap; tidak ada pembatas zoom.
- R-40 PASS: grafik memesan tinggi 180 px, nilai memuat memesan ruang, script lokal memakai defer, tanpa gambar hero/iframe/font jarak jauh pada dashboard. Tidak melaporkan metrik performa yang belum diukur.

## Delivery Gate: purpose gate

- R-01 PASS: navy menghubungkan bahan ajar; amber hanya menandai ambang/error. Alasan ada pada `DESIGN.md`; tanpa gradien.
- R-04 PASS: tidak memakai ikon dekoratif atau pustaka ikon.
- R-06 PASS: Arial untuk data/kontrol dan Georgia untuk judul catatan kuliah; alasan tertulis, tanpa unduhan font.
- R-07 PASS: latar polos memisahkan bidang baca; garis pada grafik menunjukkan skala, tanpa pola latar dekoratif.
- R-08 PASS: tidak menambah panah dekoratif pada tombol.
- R-09 PASS: status berupa teks hasil data, tanpa badge/pill di atas judul.
- R-10 PASS: tidak memakai kaca atau backdrop blur.
- R-12 PASS: bidang baca dibedakan lewat ruang/latar; tanpa bayangan besar. Bayangan inset hanya menandai tombol ditekan.
- R-13 PASS: tidak memakai glow.
- R-14 PASS: pembacaan dominan, kendali lebih sempit, tabel penuh; tidak ada kartu fitur seragam.
- R-19 PASS: MOTION 1, tanpa animasi otomatis atau pulse. Polling data dapat dijeda, dan reduced-motion dihormati.
- R-22 PASS: tidak memakai ilustrasi pengisi.

## Delivery Gate: liveliness

- L-1 PASS: ENERGY 1 / RHYTHM 2 / MOTION 1 dinyatakan pada `DESIGN.md`.
- L-2 PASS: energi rendah sesuai lembar praktikum; ritme berubah dari filter ke pengamatan/kendali lalu bukti tabel, tanpa animasi.
- L-3 PASS: suhu dan kelembapan terbaru menjadi pusat perhatian, dengan status kiriman di dekatnya.
- L-4 PASS: jarak memisahkan pemilihan, pembacaan, kendali, dan pembuktian; ruang menyempit pada ponsel.
- L-5 PASS: amber dipakai pada peringatan, dengan teks yang menjelaskan artinya; fokus teal hanya pada interaksi keyboard.
- L-6 PASS: judul serif dan bidang baca seperti catatan laboratorium dipertahankan pada halaman utama serta latihan.
- L-7 PASS: Design Read tertulis sebelum pembuatan; alasan komposisi mengikuti pembacaan sensor dan konfirmasi GPIO.

## Delivery Gate: craftsmanship dan quality locks

- C-1 PASS: keputusan warna, jenis huruf, grafik terpisah, dan perintah/konfirmasi mempunyai alasan pada desain.
- C-2 PASS: tindakan UI diuji terhadap respons API atau navigasi nyata; tidak ada tombol pengisi.
- C-3 PASS: tiap bagian membantu memilih node, membaca sensor, mengirim kendali, atau memeriksa bukti; tanpa bagian promosi.
- C-4 PASS: keadaan kosong/memuat/gagal, kedua tema, empat lebar, dan keyboard diperiksa; keterbatasan audit dijelaskan pada verifikasi.
- C-5 PASS: snapshot SQL, CSV asli, ID perintah, hasil test, serta hash sumber disertakan untuk mendukung laporan.
- R-05 PASS: RHYTHM 2 memakai filter, area pengamatan dominan, kendali, lalu tabel; tidak memakai susunan hero/kartu promosi.
- R-11 PASS: bidang isi bersudut biasa, input 3 px, tombol 4 px; tidak semua elemen dijadikan pill.
- R-15 PASS: label tindakan spesifik: Perbarui data, Simpan ambang, Nyalakan/Matikan LED, Unduh CSV.
- R-16 PASS: judul dan instruksi menyebut tugas sensor/API; pemindaian tidak menemukan slogan pemasaran atau jargon AI.
- R-20 PASS: satuan DHT22, GPIO 23, waktu kiriman, ID MySQL, dan status konfirmasi membentuk hierarki khusus praktikum IoT.
- R-21 PASS: terang menjadi awal tanpa preferensi tersimpan; tema gelap opsional dan berfungsi, pilihan dapat diubah kembali.
- R-29 PASS: token inti berupa bidang netral dan navy, amber untuk kondisi serta teal untuk fokus; dua tema didefinisikan eksplisit.
- R-30 PASS: komposisi mengikuti tugas lab; tidak menyalin produk komersial atau shell sidebar/statistik generik.
- R-31 PASS: tabel keputusan pada `DESIGN.md` menjelaskan tiap keputusan visual utama dalam satu baris.

## Bahasa dan langkah belajar

- PASS: nama Laravel, MySQL, PlatformIO, Wokwi, API, endpoint, dan identifier dipertahankan; penjelasan memakai kata kerja langsung dan padanan yang lazim.
- PASS: urutan 1 sampai 16 berlanjut dari health, POST tanpa simpan, MySQL, ESP32, Blade, JSON, grafik, perintah, hingga konfirmasi; tahap lanjut tidak mendahului bukti tahap dasar.
- PASS: panduan menyebut folder terminal, berkas, cuplikan bagian kecil, hasil yang diharapkan, dan pemeriksaan sebelum lanjut. Cuplikan ditandai agar tidak disalin sebagai program lengkap.
- PASS: persiapan backend dipisahkan dari pembacaan firmware; GPIO, library JSON, bentuk respons, dan waktu berlaku dijelaskan sebelum kendali penuh.
- PASS: pemetaan keenam topik menyebut bagian yang dapat dipakai dan pekerjaan kelompok yang masih diperlukan; contoh satu LED tidak diklaim memenuhi seluruh proyek.

Uji keterpahaman dengan mahasiswa belum dilakukan. Pemeriksaan zoom 200%, pembaca layar, dan performa lapangan belum dilakukan; laporan tidak menyatakan sertifikasi aksesibilitas penuh.

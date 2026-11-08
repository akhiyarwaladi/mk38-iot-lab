# Pemeriksaan tampilan dan urutan praktik aktuator

Lingkup: halaman `/aktuator`, API/firmware tambahan, dan panduan `AKTUATOR_BERTAHAP.md`. Antislop mode `during` mengikuti pilihan pengguna. Arah desain mewarisi `DESIGN.md` dashboard yang sudah digunakan: ENERGY 1 / RHYTHM 2 / MOTION 1. Bahasa ditinjau dengan bahasa-inti, panduan EYD untuk tulisan teknis, dan no-ai-slop. Tinjauan langkah dilakukan kembali oleh subagen; koreksinya mencakup referensi objek/callback, pendaftaran manual versus laporan boot, sesi konfirmasi, waktu expiry, dan folder terminal saat restart.

## Hard gate

- R-02 PASS: teks tambahan tidak menggunakan em dash; perintah dan pengenal kode dipertahankan.
- R-03 PASS: uji browser 360/768/1280 px pada dua tema tidak menghasilkan overflow dokumen. Tabel mempunyai area geser sendiri.
- R-17 PASS: nilai, ID, dan waktu berasal dari Laravel/MySQL, dengan masukan operator yang dicatat pada laporan uji.
- R-18 PASS: tidak ada testimoni atau identitas pelanggan rekaan.
- R-23 PASS: aset tambahan berupa screenshot praktik yang diminta; identitas dan navigasi mengikuti aplikasi lab yang tersedia.
- R-24 PASS: kedua tujuan navigasi, `/dashboard` dan `/latihan/tabel`, mengembalikan HTTP200.
- R-25 PASS: seluruh warna memakai token `dashboard.css`; 22 pasangan warna telah diperiksa pada `dashboard_contrast.json`. Tidak ada pasangan warna baru.
- R-26 PASS: pilih aktuator, perbarui, otomatis, tema, nyala/mati, dan kirim sudut mempunyai perilaku nyata pada laporan browser.
- R-27 PASS: keadaan memuat, daftar kosong, laporan lama, jaringan gagal, dan pemulihan diuji. Nilai lama tetap diberi penjelasan saat API putus.
- R-28 PASS: tidak ada FAQ pengisi.
- R-32 PASS: tombol/input/select native, label terlihat, skip link dan fokus keyboard tersedia; aktivasi melalui keyboard diperiksa.
- R-33 PASS: Blade, PHP, C++, CSS, dan JavaScript ditulis pada sumbernya. Generator hanya menyelaraskan panduan dengan LaTeX, bukan menambal antarmuka.
- R-34 PASS: tema terang/gelap memakai token yang sama; screenshot kedua tema tersedia pada tiga lebar.
- R-35 PASS: suite lama 12 uji/105 assertion, suite aktuator 12 uji/116 assertion, tiga build, serta perintah browser dengan konfirmasi real Wokwi diperiksa terpisah.
- R-36 PASS: batas penggunaan lokal, autentikasi yang belum tersedia, dan ketiadaan umpan balik mekanis dinyatakan.
- R-37 PASS: halaman tambahan mengikuti arah dashboard yang sudah ditetapkan pada `DESIGN.md`; pusat perhatian adalah target dan laporan, lalu kendali dan bukti tabel.
- R-38 PASS: angka adalah hasil uji, bukan data lapangan. Nilai awal null ditampilkan sebagai belum ada.
- R-39 PASS: judul, lang=id, landmark, label, elemen native, fokus, hover, disabled, serta kontrol pembaruan tersedia. Form servo memakai batas dan langkah bilangan bulat.
- R-40 PASS: angka memesan tinggi tampilan, skrip lokal memakai defer, dan halaman tidak memuat media/font pihak ketiga atau klaim performa.

## Purpose gate

- R-01 PASS: navy mempertahankan identitas seri; amber menjelaskan laporan lama/error, tanpa gradien.
- R-04 PASS: tidak ada ikon dekoratif.
- R-06 PASS: Arial untuk angka/kontrol dan Georgia untuk judul mengikuti dashboard, tanpa unduhan font.
- R-07 PASS: bidang polos memisahkan baca/kendali/riwayat; tanpa kisi latar.
- R-08 PASS: tidak ada panah dekoratif pada tombol.
- R-09 PASS: status disampaikan sebagai teks perintah, tanpa badge pemasaran.
- R-10 PASS: tidak memakai kaca atau backdrop blur.
- R-12 PASS: bidang dibedakan dengan ruang dan latar; tidak ada bayangan besar.
- R-13 PASS: tidak memakai glow.
- R-14 PASS: bidang nilai lebih luas, kendali lebih sempit, dan tabel memakai lebar penuh sesuai tugasnya.
- R-19 PASS: tidak ada animasi otomatis; pembaruan dua detik dapat dijeda.
- R-22 PASS: tidak memakai ilustrasi pengisi.

## Liveliness dan mutu pengerjaan

- L-1 PASS: dials ENERGY 1 / RHYTHM 2 / MOTION 1 tetap sama dengan arah dashboard.
- L-2 PASS: komposisi berganti dari pemilihan ke perbandingan nilai, kendali, dan penelusuran ID.
- L-3 PASS: target dan laporan firmware menjadi pusat perhatian layar.
- L-4 PASS: jarak memisahkan pengamatan, pengiriman, dan bukti; susunan menjadi satu kolom pada ponsel.
- L-5 PASS: amber menandai laporan lama; fokus teal menandai interaksi keyboard.
- L-6 PASS: judul catatan kuliah dan angka/tabel mempertahankan identitas praktikum.
- L-7 PASS: keputusan mengikuti arah desain dashboard yang telah tersedia sebelum halaman tambahan disusun.
- C-1 PASS: perbandingan target/laporan dan pemisahan riwayat mempunyai tujuan pembelajaran yang tertulis pada desain.
- C-2 PASS: tidak ada kontrol pengisi; tindakan diperiksa lewat HTTP/SQL atau navigasi.
- C-3 PASS: setiap bidang membantu memilih output, mengirim perintah, atau memeriksa bukti.
- C-4 PASS: keadaan kosong/error, tiga lebar, kedua tema, dan keyboard diperiksa pada laporan browser.
- C-5 PASS: hasil uji dan screenshot mempunyai sumber terpisah; batas simulasi dinyatakan.
- R-05 PASS: urutan bidang mengikuti praktik pengamatan dan penelusuran ID, tanpa susunan halaman promosi.
- R-11 PASS: input 3 px dan tombol 4 px mengikuti token dashboard; bidang data tidak dijadikan pill.
- R-15 PASS: label tindakan menyebut tugas, seperti Kirim sudut dan Matikan LED.
- R-16 PASS: teks menjelaskan nilai, waktu, dan tindakan tanpa slogan AI atau pemasaran.
- R-20 PASS: ID aktuator/perintah, sesi boot, derajat, GPIO, dan bukti SQL membentuk tampilan khusus lab IoT.
- R-21 PASS: tema terang menjadi awal; tema gelap opsional dan dapat dibalik.
- R-29 PASS: memakai bidang netral/navy, amber kondisi, dan teal fokus yang telah diuji.
- R-30 PASS: tampilan mengikuti dashboard praktikum yang sama, tanpa meniru produk komersial.
- R-31 PASS: alasan komposisi, warna, dan tipografi tertulis pada `DESIGN.md`.

## Bukti dan batas

`bukti/aktuator_verifikasi.json` mengikat hash sumber, hasil PHPUnit, build, laporan browser, dan screenshot. `bukti/actuators_live.json` mencatat perintah yang dikonfirmasi firmware Wokwi melalui Laravel/MySQL. `bukti/actuators_ui.json` memisahkan uji jaringan/daftar kosong yang disuntikkan pada browser. Angka sudut adalah setelan PWM firmware, bukan pengukuran posisi mekanis. Belum ada uji perangkat fisik atau studi pemahaman mahasiswa.

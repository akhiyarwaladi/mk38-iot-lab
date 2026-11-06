# Dari satu catatan ke ringkasan metrik

Prasyaratnya adalah Python 3, sebuah CSV berisi percobaan, dan rumus metrik dari brief. Tidak perlu memasang paket Python tambahan. `rencana_metrik.csv` dipakai untuk merencanakan pengukuran; file itu bukan masukan script analisis. Untuk data yang akan dianalisis, salin header contoh mode yang sesuai lalu isi dengan percobaan sendiri.

## 1. Baca satu baris sebelum menghitung

Buka `contoh_sintetis/klasifikasi.csv`. Baris pertama menentukan nama kolom; baris berikutnya merupakan satu percobaan. `csv.DictReader` mengubahnya menjadi dictionary sehingga `row['acuan']` dan `row['hasil']` dapat dibaca menurut nama, bukan nomor kolom.

Pada fungsi `baca()`, perhatikan urutannya: buka berkas, periksa header, baca baris, lalu periksa jumlah kolom, ID unik, dan lingkungan. Fungsi berhenti jika data belum dapat ditafsirkan. `utf-8-sig` menerima CSV UTF-8 yang memakai BOM maupun tanpa BOM.

Sebelum lanjut, tunjukkan baris yang membandingkan `terisi` dengan `kosong`; baris itu harus tetap masuk perhitungan sebagai tidak cocok.

## 2. Hitung satu metrik paling sederhana

Pada cabang `klasifikasi` dalam `hitung()`, inti hitungannya adalah:

```python
correct = sum(row['acuan'] == row['hasil'] for row in rows)
```

Setiap perbandingan bernilai benar atau salah. `sum` menghitung yang benar. Pada contoh terdapat tiga hasil cocok dari empat percobaan, sehingga `100 * 3 / 4` menghasilkan 75%. Hasil sensor yang tidak terbaca tetap dicatat, misalnya dengan label `TIDAK_TERBACA`, agar kegagalan tidak hilang dari penyebut.

Cuplikan ini adalah bagian dari fungsi lengkap, bukan program terpisah. Buka `hitung_metrik.py` untuk melihat validasi sebelum perhitungan dan dictionary hasilnya.

## 3. Tambahkan durasi serta kegagalan

Pada mode latensi, angka durasi dikumpulkan untuk baris `LULUS`. Baris `GAGAL/TIMEOUT` tetap dihitung sebagai percobaan, tetapi durasinya tidak dibuat menjadi nol. Dua respons 100 dan 1100 ms mempunyai rata-rata 600 ms; jika satu percobaan lain timeout, hanya satu dari tiga percobaan yang berhasil dalam batas 1000 ms.

Fungsi `angka()` menolak NaN, Infinity, nilai negatif, atau durasi sukses yang kosong. Setelah durasi sukses diurutkan, p95 memakai indeks `ceil(0.95 * n) - 1`. Untuk 20 durasi berurutan 1 sampai 20 ms, p95 adalah durasi ke-19. Ini ringkasan data yang dicatat; script belum mengukur waktu komunikasi sendiri.

## 4. Bandingkan skenario dan jalankan CLI

Pada mode perbandingan, tiap ID harus mewakili satu skenario dengan masukan sama pada timer tetap dan adaptif. Rumusnya `(rata_rata_tetap - rata_rata_adaptif) / rata_rata_tetap * 100`. Contoh menghasilkan `(15000 - 11000) / 15000 * 100`, sekitar 26,67%. Angka negatif tetap ditampilkan bila hasil adaptif lebih lambat.

Terakhir, baca `main()`: `argparse` memilih mode dan file; `hitung()` mengembalikan hasil; `json.dumps` mencetaknya. Kesalahan format menghasilkan kode keluar 1 serta pesan JSON. Coba tiga perintah pada modul, periksa satu hasil secara manual, lalu jalankan salinan CSV pengukuran kelompok dengan header yang sama. Catat metode pengukuran dan versi secara terpisah dari hasil hitung.

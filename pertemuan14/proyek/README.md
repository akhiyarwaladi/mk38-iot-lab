# Menghitung hasil pengujian

Ikuti [urutan membaca kode](BACA_KODE.md) untuk memahami pembacaan CSV, validasi, dan rumus sebelum membuka seluruh script.

Isi rencana metrik dengan target dari brief topik. Catat metode, versi, lingkungan, dan lokasi data mentah sebelum mulai. Folder `contoh_sintetis` berisi angka buatan untuk latihan hitung, bukan hasil simulator, perangkat fisik, atau proyek mahasiswa.

Dari folder `praktik`, coba tiga perintah pada modul. Hasil yang diharapkan:

- Klasifikasi: 3 dari 4 label cocok, akurasi 75%.
- Latensi: 2 respons berhasil dan 1 timeout; rata-rata respons 600 ms, maksimum/p95 1100 ms; hanya 1 dari 3 percobaan berhasil dalam batas 1000 ms.
- Perbandingan: rata-rata timer tetap 15000 ms dan adaptif 11000 ms; penurunan sekitar 26,67%.

Gunakan header yang sama pada CSV pengukuran sendiri. `lingkungan` harus salah satu `SINTETIS`, `SIMULASI`, atau `HARDWARE`; hasil dari lingkungan berbeda dihitung terpisah. ID harus unik. Durasi berasal dari satu metode/jam ukur, bukan selisih jam perangkat yang berbeda. P95 memakai nearest rank pada respons yang berhasil; jumlah gagal tetap dilaporkan agar timeout tidak hilang dari kesimpulan.

Klasifikasi memerlukan keadaan acuan yang dicatat secara terpisah. Perbandingan memakai pasangan skenario dengan masukan sama. Script hanya menghitung angka pada CSV dan belum memverifikasi bahwa percobaannya dilakukan dengan benar.

Untuk Greenhouse, hitung waktu di dalam rentang / seluruh waktu pengamatan, dengan memperhitungkan selang antarpengamatan. Persentase jumlah sampel hanya setara jika intervalnya seragam dan metode itu dinyatakan. Untuk Health Monitoring, laporkan selisih per pasangan bacaan dengan alat pembanding serta kesinambungan data; contoh DHT22 bukan validasi sensor BPM/SpO2.

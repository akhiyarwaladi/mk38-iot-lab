# Kendali lokal dengan dua ambang

Latihan LED sebagai indikator, memakai DHT22 GPIO 15 dan LED aktif HIGH GPIO 23. Tidak ada koneksi Wi-Fi atau MQTT pada proyek ini. Buka folder ini di VS Code, jalankan `pio run`, lalu `Wokwi: Start Simulator`.

1. Baca tabel transisi pada pertemuan 12 dan `include/aturan.h`.
2. Periksa pesan `UJI ATURAN 10/10 LULUS; GPIO=LOW` saat boot. Pemeriksaan menguji batas, keadaan sebelumnya, NaN, rentang sensor, serta baca GPIO.
3. Ubah suhu DHT22 secara berurutan menjadi 27, 30, 29, dan 28 °C. Harapan: mati, nyala, tetap nyala, lalu mati.
4. Cocokkan nilai Serial dan LED. Simpan screenshot serta versi firmware.
5. Baru setelah hasilnya cocok, rancang penggabungan dengan komunikasi. Pembacaan/keputusan lokal tidak boleh terlewati hanya karena loop jaringan keluar saat Wi-Fi putus. Tentukan prioritas manual/otomatis sebelum menggabungkan tombol.

Nilai 30/28 °C dan keadaan mati saat sensor gagal adalah aturan contoh, bukan rekomendasi untuk pompa, lalu lintas, atau perangkat kesehatan. Firmware gabungan kelompok harus diuji lagi; contoh lokal tidak membuktikan MQTT atau cloud tetap bekerja.

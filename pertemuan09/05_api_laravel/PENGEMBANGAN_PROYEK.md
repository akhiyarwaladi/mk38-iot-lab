# Menggunakan API sebagai dasar proyek akhir MK38

Acuan: [salinan brief proyek yang memuat enam topik](referensi/project_brief.tex), proposal pertemuan 11, dan RPS MK38. Brief ini menetapkan enam kelompok dengan lima mahasiswa, milestone desain 10%, proyek akhir 40%, fitur tingkat 1 serta minimal dua pilihan tingkat 2. Salinan sumber disertakan agar brief tetap dapat dibaca setelah ZIP diekstrak; asalnya dijelaskan pada [catatan referensi](referensi/README.md). Berkas `final_project_brief.tex` yang menyebut 23% dan kelompok 3 sampai 4 orang adalah versi berbeda yang tidak dipakai untuk pemetaan ini.

Brief menilai alur sensor sampai dashboard dan kendali balik, desain perangkat, hasil pengujian, serta kontribusi anggota. Dashboard Laravel menyediakan dasar untuk mengamati alur itu: data MySQL, grafik, riwayat, ekspor CSV, dan kendali satu LED dengan konfirmasi. Ini contoh pembelajaran bersama; spesifikasi sensor dan fungsi inti setiap topik tetap harus dikerjakan kelompok.

## Fungsi yang dapat dibangun dari API

| Fungsi | Contoh dalam lab | Kegunaan dalam proyek |
|---|---|---|
| Pemantauan | Suhu dan kelembapan terakhir, dipilih menurut `device_id` | Memeriksa node yang benar, bukan mencampur data antarnode. |
| Grafik riwayat | Sumbu waktu penerimaan dan skala terpisah | Melihat perubahan setelah masukan sensor atau kondisi uji diubah. |
| Status kiriman | Baru diterima atau belum ada kiriman baru setelah 30 detik | Membedakan nilai terakhir dengan perangkat yang masih aktif mengirim. |
| Aturan indikator | Ambang suhu yang disimpan di MySQL | Memisahkan konfigurasi dari kode tampilan; ambang masih berupa aturan latihan. |
| Kendali balik | Perintah LED, waktu berlaku, pengambilan oleh ESP32, konfirmasi | Membuktikan aplikasi dapat memengaruhi aktuator dan menerima laporan hasilnya. |
| Log perintah | Menunggu, dikonfirmasi, diganti, kedaluwarsa | Menelusuri kegagalan kendali tanpa menganggap klik tombol sebagai keberhasilan. |
| Ekspor bukti | CSV berisi catatan yang sama dengan pilihan grafik/tabel | Menghitung metrik dan menyertakan data yang dapat diperiksa pada laporan. |

## Pemetaan ke enam topik

| Topik brief | Bagian yang dapat digunakan kembali | Bagian yang perlu dibangun kelompok |
|---|---|---|
| Smart Parking | Identitas node, riwayat peristiwa, log perintah, tampilan | Data 4 sampai 6 slot, sesi masuk/keluar, palang servo, MQTT, serta pembayaran sandbox bila memilih fitur bonus. Tambahkan tabel slot dan sesi, jangan menyimpan okupansi sebagai “suhu”. |
| Smart Greenhouse | DHT22, grafik, ambang yang dapat diubah, riwayat dan CSV | Kelembapan tanah, tangki/LDR, pompa dan kipas, keputusan otomatis lokal, MQTT, serta notifikasi sesuai fitur yang dipilih. Ambang tanah memakai satuan/rentang sendiri. |
| Smart Home | Kendali aplikasi, konfirmasi aktuator, log aktivitas, DHT22 | Tiga sampai empat aktuator, PIR, mode otomatis, MQTT telemetri, serta sedikitnya dua fitur tingkat 2. LED tunggal di lab belum memenuhi spesifikasi tersebut. |
| Adaptive Traffic Light | Riwayat, visualisasi fase/antrean, ekspor untuk analisis | Pengendali empat lengan, sensor antrean, transisi all-red, algoritma prioritas, dan MQTT. Siklus lampu berjalan pada pengendali lokal; dashboard dipakai untuk observasi dan uji. |
| Flood Warning | Grafik historis, pengelompokan node, indikator dan log | Ketinggian air, sensor hujan, klasifikasi level, pola buzzer, Telegram, dan MQTT. Terapkan filter/debounce pada sensor; jangan menganggap indikator suhu sebagai logika banjir. |
| Health Monitoring | Identitas perangkat, grafik tren, penyimpanan dan ekspor | Sensor BPM/SpO2/suhu, tampilan lokal, MQTT, serta fitur tingkat 2 yang dipilih. Gunakan data uji untuk demonstrasi perangkat; dashboard lab bukan alat diagnosis. |

Beberapa topik mewajibkan MQTT. Dashboard REST ini tidak menggugurkan ketentuan itu. Kelompok dapat memakai firmware publish/subscriber pertemuan 10 atau integrasi pertemuan 11 sebagai jalur MQTT, lalu menyimpan hasilnya melalui satu layanan data. Tentukan satu jalur pencatatan agar pembacaan yang sama tidak masuk dua kali melalui MQTT dan REST.

## Urutan pengerjaan untuk kelompok

1. Jalankan API dan tabel sensor sampai data tersimpan; catat ID yang cocok antara respons dan MySQL.
2. Jalankan dashboard untuk satu node. Ubah masukan sensor dan buktikan grafik serta CSV berubah.
3. Jalankan firmware kendali. Bandingkan perintah yang masih menunggu dengan perintah yang sudah dikonfirmasi ESP32.
4. Rumuskan kontrak data topik kelompok: nama field, tipe, satuan, batas input, ID node, timestamp, dan format konfirmasi. Buat migration baru untuk field/topik tersebut.
5. Tambahkan sensor dan aktuator satu per satu. Pertahankan fungsi inti lokal jika topik meminta mode offline.
6. Integrasikan MQTT, keamanan, dan layanan eksternal sesuai brief. Siapkan bukti setiap tahap sebelum menggabungkan seluruh fungsi.
7. Ukur metrik topik dan tulis batas hasilnya. Setelah simulasi lulus, lanjutkan perakitan, enclosure, serta pengujian perangkat fisik sesuai arahan pengajar.

REST polling pada firmware contoh dijadwalkan sekitar satu detik, tetapi permintaan HTTP, pembacaan sensor, dan jaringan dapat menambah waktu tunggu. Hasilnya belum membuktikan target kendali satu detik dalam brief Smart Home. Untuk target tersebut, gunakan jalur MQTT yang sesuai, ukur dari permintaan sampai konfirmasi, dan laporkan distribusi waktunya.

## Bukti yang dapat dihasilkan dari contoh ini

| Kasus uji | Kriteria penerimaan | Bukti |
|---|---|---|
| Sensor berubah | Nilai baru mempunyai ID tersimpan dan muncul pada grafik | Screenshot, ID respons, SELECT MySQL, CSV. |
| Input di luar rentang | API menolak dengan 422 tanpa catatan sensor baru | Body permintaan, respons, jumlah baris sebelum/sesudah. |
| LED nyala/mati | ESP32 menerapkan GPIO dan melaporkan konfirmasi dengan ID perintah yang sama | Log Serial, status dashboard, catatan `commands`. |
| Perangkat berhenti | Status kiriman menjadi lama; perintah tidak diberi status dikonfirmasi tanpa laporan | Screenshot setelah batas waktu serta log perintah kedaluwarsa. |
| API dimulai ulang | Sensor, konfigurasi, dan riwayat perintah tetap tersimpan | Pembacaan ID sebelum/sesudah restart. |

Konfirmasi firmware menunjukkan nilai GPIO yang dilaporkan program. Untuk aktuator fisik, tambahkan pengamatan atau sensor umpan balik yang sesuai; respons API saja tidak membuktikan motor, pompa, atau relay benar-benar bekerja.

## Pembagian hasil kerja lima anggota

| Peran | Hasil kerja yang diperiksa |
|---|---|
| Sensor dan rangkaian | Pemetaan pin, satuan, kalibrasi bila diperlukan, hasil simulasi dan perakitan. |
| Firmware | Pembacaan sensor, kendali lokal, komunikasi, dan konfirmasi hasil aktuator. |
| API dan database | Kontrak endpoint, migration, validasi, penyimpanan, dan konfigurasi layanan. |
| Dashboard | Grafik, filter, kondisi koneksi, kendali, serta tampilan hasil yang jujur. |
| Pengujian dan dokumentasi | Kasus uji, data mentah, metrik, video cadangan, serta README replikasi. |

Setiap anggota tetap mempelajari keseluruhan alur. Deklarasikan pemakaian alat bantu AI pada laporan sesuai brief, dan jelaskan perubahan yang benar-benar dibuat kelompok.

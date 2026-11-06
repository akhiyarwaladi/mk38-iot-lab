# Arah dashboard praktikum MK38

Dashboard untuk mahasiswa yang memeriksa alur sensor, penyimpanan, dan kendali balik pada proyek IoT. Contoh memakai suhu, kelembapan, dan satu LED dari rangkaian pertemuan 9. Pemantauan dan konfirmasi perangkat menjadi fokus.

ENERGY 1 / RHYTHM 2 / MOTION 1. Tiga bagian mengikuti keputusan pengguna: pilih perangkat dan baca kondisi, lihat perubahan pada grafik, lalu periksa hasil kendali dan bukti riwayat. Tidak memakai animasi otomatis.

| Keputusan | Alasan |
|---|---|
| Navy dari seri modul, tinta gelap, putih; amber hanya untuk peringatan | Menjaga identitas bahan ajar dan membedakan kondisi yang perlu diperiksa. |
| Arial untuk kontrol/data, Georgia untuk judul halaman | Angka dan formulir mudah dibaca; judul mengikuti watak catatan kuliah tanpa mengunduh font. |
| Satu area pembacaan dominan, grafik di samping kendali, riwayat di bawah | Urutan membaca mengikuti pengamatan, tindakan, lalu pembuktian hasil. |
| Grafik suhu dan kelembapan terpisah | Satuan dan skala keduanya berbeda; satu sumbu campuran dapat menyesatkan. |
| Tombol perintah berbeda dari status konfirmasi | Respons API 202 berarti antrean tersimpan, bukan LED sudah berubah. |
| Tema terang dan gelap dengan kontrol nyata | Mahasiswa dapat menyesuaikan layar tanpa mengubah arti status atau data. |
| Tanpa logo baru, ilustrasi, ikon, kartu pemasaran, dan data pengisi | Isi berasal dari database praktikum; elemen tambahan tersebut tidak membantu keputusan pemantauan. |

Warna, kontras, fokus keyboard, lebar ponsel, kondisi kosong, loading, error, dan tiap kontrol diperiksa sebelum penyerahan. Angka yang ditampilkan berasal dari MySQL. Ambang suhu 30 °C adalah aturan latihan yang dapat diganti, bukan acuan keselamatan ruangan.

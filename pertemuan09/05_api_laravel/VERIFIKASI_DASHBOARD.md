# Hasil uji dashboard dan kendali ESP32

Diuji pada 6 November 2026 dengan Laravel 12.71.0, PHP 8.2.12, MySQL Community Server 8.4.13, PlatformIO, serta Wokwi di VS Code. API memakai `127.0.0.1:8000`; MySQL lokal pengujian memakai port 3309. Port dan password pada komputer mahasiswa mengikuti pemasangan masing-masing.

## Hasil pengujian

| Pemeriksaan | Hasil dan bukti |
|---|---|
| API sensor lama dan penambahan dashboard | 12 uji Laravel, 105 assertion, tanpa gagal atau dilewati. Database uji MySQL `mk38_sensor_test` terpisah dari data simulator. Lihat `bukti/laravel_dashboard_tests.json`. |
| Input, filter, dan data lama | Uji mencakup batas input, perangkat tanpa kiriman, status setelah 31 detik, ambang tersimpan, dan pembatasan jumlah catatan. |
| Urutan perintah | Uji memeriksa pending, konfirmasi dengan nilai salah, konfirmasi ulang, ID perangkat berbeda, perintah diganti, dan perintah kedaluwarsa. Konfirmasi lama tidak boleh menimpa laporan keadaan yang lebih baru. |
| Kompilasi firmware | Keempat versi 01 sampai 04 lulus build. Versi aktif sama dengan `04_kendali.cpp`; RAM 45.892 byte dan flash 800.349 byte. Lihat `bukti/firmware_dashboard_builds.json`. |
| Kiriman simulator ke MySQL | Terdapat 244 catatan sensor setelah simulator dihentikan. Catatan awal ID 1, 49, dan 66 tetap dapat dibaca dengan nilai yang sama. Nilai terakhir 35 °C dan 75%. |
| Kendali nyala | Perintah #3 diterima melalui dashboard, diterapkan firmware, lalu berstatus `applied` dengan waktu konfirmasi di MySQL. |
| Kendali mati | Perintah #4 melalui alur yang sama; laporan LED terakhir `false`. Simulator dihentikan setelah LED kembali mati. |
| Waktu permintaan sampai konfirmasi | #3: 7,192 detik, termasuk saat memulai ulang simulator; #4: 1,496 detik. Dua pengamatan ini belum memenuhi pembuktian target kendali satu detik pada brief Smart Home. |
| CSV sesuai pilihan tampilan | Unduhan dari browser berisi 20 catatan, ID 217 sampai 236. Himpunan ID sama dengan tabel yang dijeda. Tabel terbaru di atas; CSV lama ke baru. Tiap nilai CSV dibaca ulang melalui GET. |
| Kesalahan koneksi nyata | Server API dihentikan saat halaman terbuka. Pesan gagal muncul dan menyebut bahwa nilai lama masih ditampilkan. Server dijalankan lagi dan pembacaan pulih. |
| Tampilan dan keyboard | Lebar 320, 390, 768, dan 1280 piksel diperiksa; tidak ada overflow halaman. Tema terang/gelap, keadaan kosong, Tab, Space untuk tema, serta fokus 3 px diperiksa. |
| Kontras | 22 pasangan warna dari CSS lulus batas yang diperiksa. Rasio teks terendah 5,74:1. Lihat `bukti/dashboard_contrast.json`. |

Hasil SQL, respons API, waktu perintah, dan hash sumber tersimpan pada `bukti/live_dashboard_result.json`. Pemeriksaan browser tersimpan pada `bukti/browser_dashboard_checks.json`. Tangkapan layar pada folder yang sama memperlihatkan data nyata dari pengujian simulator.

Saat pengujian berlangsung lama, log server yang dialirkan ke proses pengujian sempat menumpuk dan membuat request menunggu. Server kemudian dijalankan dengan keluaran log ke berkas. Firmware akhir memakai timeout koneksi 2 detik dan baca 3 detik; kendali nyala dan mati diuji ulang sesudah perbaikan tersebut. Waktu HTTP tetap dapat memengaruhi jadwal polling.

## Mengulang pemeriksaan

Setelah menyiapkan database **khusus uji**, jalankan dari `backend`:

```powershell
php artisan test --no-ansi
```

Petunjuk `.env.testing` ada pada `backend/README.md`. Uji Laravel membuat ulang tabel pada `mk38_sensor_test`; guard menolak nama database lain. Untuk kompilasi empat versi, jalankan dari `api_sensor` dengan Python dan PlatformIO yang tersedia:

```powershell
python tests/build_versions.py --pio "C:/lokasi/platformio.exe" --output build/firmware
python tests/check_dashboard_contrast.py
```

Pemeriksa data yang sudah ada tidak membuat perintah atau catatan sensor. Setelah menjalankan uji nyala dan mati sendiri, berikan ID yang benar dari sesi tersebut:

```powershell
python tests/verify_dashboard_live.py --php php --on-id 3 --off-id 4
```

Contoh ID 3/4, data lama, dan CSV pada pemeriksa itu merujuk sesi bukti pengajar. Pada database baru, jalankan skenario yang sama dan sesuaikan catatan bukti terlebih dahulu; angka ID tidak dijamin sama. `tests/package_lab.py` memeriksa kecocokan bukti dengan sumber sebelum membuat ZIP.

## Batas hasil

Firmware kendali akhir sudah dioperasikan di Wokwi. Tiga versi pengantar lulus kompilasi; masing-masing belum dijalankan terpisah pada sesi dashboard. Pengujian pada ESP32 fisik, MQTT, server internet, HTTPS, autentikasi perangkat, dan beberapa pengguna serentak belum dilakukan pada lab ini. Konfirmasi GPIO berasal dari firmware; pengujian aktuator fisik memerlukan umpan balik yang sesuai.

Audit tampilan ini memeriksa kondisi dan ukuran layar yang disebutkan, bukan sertifikasi WCAG penuh. Zoom browser 200%, pembaca layar, serta metrik Lighthouse/Core Web Vitals belum diukur. Uji pemahaman mahasiswa juga belum dilakukan. Panduan bertahap diperiksa dari persiapan, berkas yang dibaca, cuplikan kode, tindakan, dan bukti sebelum melanjutkan.

Catatan uji awal sensor tetap disimpan pada `VERIFIKASI.md`, `bukti/live_result.json`, `bukti/laravel_tests.json`, dan `bukti/firmware_builds.json`. Gunakan berkas bernama `dashboard` untuk hasil dashboard. Edisi 7 November memasukkan tutorial ini ke dalam PDF pertemuan 9, tahap 3 sampai 8, beserta tautan kode GitHub. Halaman `/latihan/nilai` ditambahkan di antara tabel Blade dan dashboard lengkap untuk mengajarkan satu pembacaan JSON. Bukti kendali simulator di atas tetap merujuk sesi 6 November; pembacaan ulang bukti tidak dianggap sebagai sesi kendali baru.

`tests/package_lab.py` adalah alat pengemasan pengajar di repositori akreditasi, bukan langkah instalasi mahasiswa dari repo praktikum. Untuk menjalankan aplikasi, ikuti `README.md` dan `backend/README.md`.

Uji salinan bersih juga memeriksa berkas yang tidak terwakili oleh folder
kerja pengajar. `.env.example` kini wajib disertakan dalam paket. Referensi
suite Unit yang kosong dihapus dari `phpunit.xml`; seluruh 12 pengujian
berada pada suite Feature. Hasil pemasangan dan tahapan HTTP dicatat
terpisah pada `PEMASANGAN_API_BERSIH.json` di paket seri.

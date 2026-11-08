from urllib.parse import urlencode
from http_json import minta
from konfigurasi import ID_AKTUATOR


def cari_id(nama):
    parameter = urlencode({"device_id": ID_AKTUATOR})
    status, daftar = minta("GET", "/api/v1/aktuator?" + parameter)
    if status != 200:
        raise SystemExit("Daftar gagal dibaca; periksa route aktuator.")
    for baris in daftar:
        if baris["name"] == nama:
            return baris["id"]
    raise SystemExit("Daftarkan " + nama + " dahulu dengan skrip 06 atau 07.")

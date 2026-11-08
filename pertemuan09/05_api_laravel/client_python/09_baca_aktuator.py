from aktuator import cari_id
from http_json import minta

for nama in ("lampu", "pintu"):
    path = "/api/v1/aktuator/" + str(cari_id(nama))
    for akhir in ("/perintah", "/riwayat"):
        status, data = minta("GET", path + akhir)
        if status != 200:
            raise SystemExit(1)

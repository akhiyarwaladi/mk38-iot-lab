from http_json import minta
from konfigurasi import ID_SENSOR

NILAI_LED = True
path = "/api/v1/perangkat/" + ID_SENSOR + "/perintah"
status, perintah = minta("POST", path, {"led": NILAI_LED})
if status != 202:
    raise SystemExit("Perintah ditolak; periksa route tahap 4 dan ID perangkat.")
status, hasil = minta("GET", path)
if status != 200:
    raise SystemExit(1)

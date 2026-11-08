from http_json import minta
from konfigurasi import ID_SENSOR

DATA = {"device_id": ID_SENSOR, "suhu": 28.0, "kelembapan": 65.0}
status, catatan = minta("POST", "/api/v1/sensor", DATA)
if status != 201:
    raise SystemExit("Belum tersimpan; aktifkan route tahap 3 dan periksa MySQL.")
status, hasil = minta("GET", "/api/v1/sensor/" + str(catatan["id"]))
if status != 200 or hasil != catatan:
    raise SystemExit("GET belum cocok dengan hasil POST.")
print("Cocok: POST 201 dan GET 200 membaca catatan yang sama.")

from aktuator import cari_id
from http_json import minta

path = "/api/v1/aktuator/" + str(cari_id("pintu")) + "/perintah"
status, hasil = minta("POST", path, {"value": 181})
if status != 422:
    raise SystemExit("Gagal: nilai 181 seharusnya ditolak HTTP 422.")
print("Sesuai: nilai di luar rentang ditolak.")

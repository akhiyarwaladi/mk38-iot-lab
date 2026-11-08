from aktuator import cari_id
from http_json import minta

NILAI = 1
id_led = cari_id("lampu")
path = "/api/v1/aktuator/" + str(id_led)
status, perintah = minta("POST", path + "/perintah", {"value": NILAI})
if status != 202:
    raise SystemExit(1)
status, riwayat = minta("GET", path + "/riwayat")
if status != 200:
    raise SystemExit(1)

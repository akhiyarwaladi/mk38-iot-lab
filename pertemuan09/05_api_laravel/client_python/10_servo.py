from aktuator import cari_id
from http_json import minta

SUDUT = 90
path = "/api/v1/aktuator/" + str(cari_id("pintu")) + "/perintah"
status, perintah = minta("POST", path, {"value": SUDUT})
if status != 202:
    raise SystemExit(1)

from urllib.parse import urlencode
from http_json import minta
from konfigurasi import ID_AKTUATOR

status, data = minta("POST", "/api/v1/aktuator",
    {"device_id": ID_AKTUATOR, "name": "pintu", "kind": "servo"})
if status not in (200, 201):
    raise SystemExit(1)
parameter = urlencode({"device_id": ID_AKTUATOR})
status, daftar = minta("GET", "/api/v1/aktuator?" + parameter)
if status != 200:
    raise SystemExit(1)

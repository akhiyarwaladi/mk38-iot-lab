from http_json import minta
from konfigurasi import ID_AKTUATOR

status, data = minta("POST", "/api/v1/aktuator",
    {"device_id": ID_AKTUATOR, "name": "lampu", "kind": "led"})
if status not in (200, 201):
    raise SystemExit(1)

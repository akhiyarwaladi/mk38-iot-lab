from urllib.parse import urlencode
from http_json import minta
from konfigurasi import ID_SENSOR

parameter = urlencode({"device_id": ID_SENSOR, "limit": 5})
status, data = minta("GET", "/api/v1/sensor?" + parameter)
if status != 200:
    raise SystemExit(1)

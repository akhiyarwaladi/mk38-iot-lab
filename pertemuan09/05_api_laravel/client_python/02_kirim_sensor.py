import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from konfigurasi import API_DASAR, ID_SENSOR

DATA = {"device_id": ID_SENSOR, "suhu": 28.0, "kelembapan": 65.0}
body = json.dumps(DATA).encode("utf-8")
permintaan = Request(API_DASAR + "/api/v1/sensor", data=body,
    headers={"Content-Type": "application/json", "Accept": "application/json"},
    method="POST")
try:
    with urlopen(permintaan, timeout=10) as respons:
        status, isi = respons.status, respons.read()
except HTTPError as galat:
    status, isi = galat.code, galat.read()
except (URLError, TimeoutError) as galat:
    raise SystemExit("Koneksi gagal: " + str(galat))
print("HTTP", status)
try:
    print(json.dumps(json.loads(isi.decode("utf-8")), indent=2))
except (ValueError, UnicodeDecodeError):
    raise SystemExit("Respons bukan JSON; periksa URL dan log Laravel.")
if status >= 400:
    raise SystemExit(1)

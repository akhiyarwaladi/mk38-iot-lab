import json
from urllib.error import URLError
from urllib.request import urlopen
from konfigurasi import API_DASAR

try:
    with urlopen(API_DASAR + "/api/v1/health", timeout=10) as respons:
        print("HTTP", respons.status)
        print(json.loads(respons.read().decode("utf-8")))
except (URLError, TimeoutError) as galat:
    raise SystemExit("Health gagal; periksa server dan URL: " + str(galat))

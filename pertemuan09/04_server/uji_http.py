import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

URL = "http://localhost:8180"
NILAI_LED = "on"
permintaan = [Request(URL + "/sensor"),
    Request(URL + "/led", data=urlencode({"state": NILAI_LED}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")]
for request in permintaan:
    try:
        with urlopen(request, timeout=10) as respons:
            print(request.get_method(), request.full_url, "-> HTTP", respons.status)
            if "application/json" in respons.headers.get("Content-Type", ""):
                print(json.loads(respons.read().decode("utf-8")))
    except HTTPError as galat:
        print("HTTP", galat.code, galat.read().decode("utf-8", errors="replace"))
        raise SystemExit(1)
    except (URLError, TimeoutError) as galat:
        raise SystemExit("Koneksi gagal; periksa Wokwi dan port 8180: " + str(galat))

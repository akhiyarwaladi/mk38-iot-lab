import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from konfigurasi import API_DASAR


def minta(metode, path, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    permintaan = Request(API_DASAR + path, data=body, method=metode,
        headers={"Accept": "application/json", "Content-Type": "application/json"})
    try:
        with urlopen(permintaan, timeout=10) as respons:
            status, isi = respons.status, respons.read()
    except HTTPError as galat:
        status, isi = galat.code, galat.read()
    except (URLError, TimeoutError) as galat:
        raise SystemExit("Koneksi gagal: " + str(galat))
    print(metode, path, "-> HTTP", status)
    try:
        data = json.loads(isi.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise SystemExit("Respons bukan JSON; periksa URL dan log Laravel.")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return status, data

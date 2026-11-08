import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:1880/api/riwayat"
try:
    with urlopen(url, timeout=10) as respons:
        print("HTTP", respons.status)
        data = json.loads(respons.read().decode("utf-8"))
        print(json.dumps(data, indent=2, ensure_ascii=False))
except HTTPError as galat:
    print("HTTP", galat.code)
    print(galat.read().decode("utf-8", errors="replace"))
    sys.exit(1)
except (URLError, TimeoutError) as galat:
    print("Koneksi gagal:", galat)
    sys.exit(1)
except (json.JSONDecodeError, UnicodeDecodeError) as galat:
    print("Respons bukan JSON UTF-8 yang valid:", galat)
    sys.exit(1)

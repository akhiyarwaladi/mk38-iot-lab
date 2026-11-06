"""Three real TLS cases against the local Mosquitto lab listener."""
import json
import os
from pathlib import Path
import uuid
from uji_tls import probe

base = Path(__file__).resolve().parent
password = os.environ.get("LOCAL_MQTT_PASSWORD")
if not password: raise SystemExit("Isi LOCAL_MQTT_PASSWORD terlebih dahulu.")
results = {}
for case, ca, key in (("valid", "runtime/ca.crt", password),
                      ("wrong_ca", "emqx-ca.crt", password),
                      ("wrong_password", "runtime/ca.crt", "salah-" + uuid.uuid4().hex)):
    results[case] = probe("localhost", 18883, base / ca, "perangkat", key,
                         "unja/mk38/p14/uji/" + uuid.uuid4().hex)
print(json.dumps(results, indent=2))
passed = results["valid"]["roundtrip"] and not results["wrong_ca"]["roundtrip"] and not results["wrong_password"]["roundtrip"]
raise SystemExit(0 if passed else 1)

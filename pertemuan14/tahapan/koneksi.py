"""Konfigurasi dan koneksi TLS yang dipakai bersama oleh latihan kecil."""
import json
import os
from pathlib import Path
import uuid
import paho.mqtt.client as mqtt


def baca_config(path):
    path = Path(path).resolve()
    return json.loads(path.read_text(encoding="utf-8")), path.parent


def buat_client(config, base, role):
    cfg = config[role]
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id="tahap-" + uuid.uuid4().hex[:12])
    client.tls_set(str(base / cfg["ca"]))
    if cfg.get("username"):
        password = os.environ.get(cfg["password_env"])
        if not password:
            raise ValueError("Isi " + cfg["password_env"])
        client.username_pw_set(cfg["username"], password)
    return client

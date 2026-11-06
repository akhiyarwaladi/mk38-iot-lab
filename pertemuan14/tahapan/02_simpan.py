"""Tahap 2: validasi satu berkas JSON dan simpan pada database latihan."""
import argparse
from datetime import datetime, timezone
import json
import math
import sqlite3
import uuid
from pathlib import Path
from koneksi import baca_config


def validasi(data):
    if not isinstance(data, dict):
        raise ValueError("JSON harus berupa object")
    for field, low, high in (("suhu", -40, 80), ("kelembapan", 0, 100)):
        value = data.get(field)
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError("Nilai tidak valid: " + field)
    if type(data.get("led")) is not bool:
        raise ValueError("led harus boolean")
    return {field: data[field] for field in ("suhu", "kelembapan", "led")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--input", type=Path, default=Path("tahapan/sampel.json"))
    args = parser.parse_args()
    _, base = baca_config(args.config)
    data = validasi(json.loads(args.input.read_text(encoding="utf-8")))
    data.update(event_id=uuid.uuid4().hex, received_at=datetime.now(timezone.utc).isoformat())
    path = base / "runtime/tahapan.sqlite"
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS samples (event_id TEXT PRIMARY KEY, received_at TEXT NOT NULL, payload TEXT NOT NULL, sent INTEGER NOT NULL DEFAULT 0)")
        db.execute("INSERT INTO samples(event_id,received_at,payload) VALUES(?,?,?)",
                   (data["event_id"], data["received_at"], json.dumps(data, allow_nan=False)))
    print("Tersimpan pada database latihan; sent=0; event_id=" + data["event_id"])


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit("Sampel ditolak: " + str(error))

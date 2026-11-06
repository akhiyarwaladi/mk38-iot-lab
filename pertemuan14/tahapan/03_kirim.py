"""Tahap 3: kirim antrean latihan sekali; tandai hanya sesudah PUBACK."""
import argparse
import sqlite3
import time
from koneksi import baca_config, buat_client

parser = argparse.ArgumentParser()
parser.add_argument("--config", default="config.json")
args = parser.parse_args()
config, base = baca_config(args.config)
path = base / "runtime/tahapan.sqlite"
if not path.is_file():
    raise SystemExit("Jalankan 02_simpan.py lebih dahulu.")
client = buat_client(config, base, "cloud")
try:
    client.connect(config["cloud"]["host"], config["cloud"]["port"], 30)
    client.loop_start()
    deadline = time.monotonic() + 10
    while not client.is_connected() and time.monotonic() < deadline:
        time.sleep(0.1)
    if not client.is_connected():
        raise SystemExit("Cloud belum tersambung; antrean tetap pending.")
    with sqlite3.connect(path) as db:
        rows = db.execute("SELECT event_id,payload FROM samples WHERE sent=0 ORDER BY rowid").fetchall()
        for event_id, payload in rows:
            info = client.publish(config["cloud"]["root"] + "/sensor", payload, qos=1, retain=False)
            info.wait_for_publish(5)
            if not info.is_published():
                raise SystemExit("PUBACK belum diterima; baris ini tetap pending.")
            db.execute("UPDATE samples SET sent=1 WHERE event_id=?", (event_id,))
            db.commit()
            print("Cloud PUBACK event_id=" + event_id, flush=True)
        print("Kiriman selesai:", len(rows))
except (OSError, RuntimeError, ValueError) as error:
    raise SystemExit("Pengiriman berhenti; periksa pending: " + str(error))
finally:
    client.disconnect()
    client.loop_stop()

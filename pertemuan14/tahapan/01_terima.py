"""Tahap 1: tampilkan pesan lokal tanpa database atau koneksi cloud."""
import argparse
from koneksi import baca_config, buat_client

parser = argparse.ArgumentParser()
parser.add_argument("--config", default="config.json")
parser.add_argument("--role", choices=("local", "cloud"), default="local")
args = parser.parse_args()
config, base = baca_config(args.config)
cfg = config[args.role]
client = buat_client(config, base, args.role)


def terhubung(client, userdata, flags, reason, properties):
    print(args.role + " CONNACK=" + str(reason), flush=True)
    if not reason.is_failure:
        client.subscribe(cfg["root"] + "/sensor", 1)


def terima(client, userdata, message):
    print(message.topic, message.payload.decode(errors="replace"), flush=True)


client.on_connect = terhubung
client.on_message = terima
try:
    client.connect(cfg["host"], cfg["port"], 30)
    client.loop_forever()
except KeyboardInterrupt:
    pass
finally:
    client.disconnect()

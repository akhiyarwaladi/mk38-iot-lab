"""Synthetic gateway input; not a physical DHT22 measurement."""
import argparse
import json
import os
from pathlib import Path
import time
import uuid
import paho.mqtt.client as mqtt
from gateway import validate

parser = argparse.ArgumentParser()
parser.add_argument('--config',type=Path,default=Path('config.json'))
parser.add_argument('--suhu',type=float,default=28)
parser.add_argument('--kelembapan',type=float,default=65)
args=parser.parse_args()
base=args.config.resolve().parent
cfg=json.loads(args.config.read_text(encoding='utf-8'))['local']
payload=json.dumps(validate(json.dumps(dict(suhu=args.suhu,kelembapan=args.kelembapan,led=False))))
client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='input-lab-'+uuid.uuid4().hex[:12])
client.tls_set(str(base/cfg['ca']))
password=os.environ.get(cfg['password_env'])
if not password:raise SystemExit('Isi '+cfg['password_env'])
client.username_pw_set(cfg['username'],password)
try:
    client.connect(cfg['host'],cfg['port'],20);client.loop_start()
    deadline=time.monotonic()+10
    while not client.is_connected() and time.monotonic()<deadline:time.sleep(.1)
    if not client.is_connected():raise SystemExit('Broker belum menerima koneksi.')
    sent=client.publish(cfg['root']+'/sensor',payload,qos=1,retain=False)
    sent.wait_for_publish(5)
    if not sent.is_published():raise SystemExit('PUBACK belum diterima.')
    print('Input sintetis gateway (bukan pengukuran hardware): '+payload)
finally:
    client.disconnect();client.loop_stop()

"""TLS MQTT gateway with SQLite outbox; delivery is at least once."""
import argparse
import json
import logging
import math
import os
from pathlib import Path
import queue
import signal
import sqlite3
import ssl
import threading
import time
import uuid
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

LOG = logging.getLogger("gateway")


def validate(payload):
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("JSON harus berupa object")
    for field, low, high in (("suhu", -40, 80), ("kelembapan", 0, 100)):
        value = data.get(field)
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError("Nilai sensor tidak valid: " + field)
    if type(data.get("led")) is not bool:
        raise ValueError("led harus boolean")
    return {field: data[field] for field in ("suhu", "kelembapan", "led")}


class Gateway:
    def __init__(self, config, base):
        self.config, self.base = config, Path(base)
        self.stop = threading.Event()
        self.inbox = queue.Queue(maxsize=1000)
        self.cloud_up = threading.Event()
        self.last_state = None
        self.state_pending = False
        db = self.base / config["database"]
        db.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db)
        self.db.execute("CREATE TABLE IF NOT EXISTS samples (event_id TEXT PRIMARY KEY, received_at TEXT NOT NULL, payload TEXT NOT NULL, sent INTEGER NOT NULL DEFAULT 0)")
        self.db.commit()
        self.local = self.make_client("local")
        self.cloud = self.make_client("cloud")

    def make_client(self, role):
        cfg = self.config[role]
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                             client_id="gw-" + role + "-" + uuid.uuid4().hex[:12])
        client.tls_set(str(self.base / cfg["ca"]), tls_version=ssl.PROTOCOL_TLS_CLIENT)
        if cfg.get("username"):
            password = os.environ.get(cfg["password_env"])
            if not password:
                raise ValueError("Isi environment variable " + cfg["password_env"])
            client.username_pw_set(cfg["username"], password)
        client.reconnect_delay_set(1, 15)

        def connected(c, userdata, flags, reason, properties):
            LOG.info("%s CONNACK=%s", role, reason)
            if reason.is_failure:
                return
            if role == "local":
                c.subscribe([(cfg["root"] + "/sensor", 1),
                             (cfg["root"] + "/led/state", 1)])
            else:
                self.state_pending = True
                self.cloud_up.set()
                if self.config.get("allow_cloud_control", False):
                    c.subscribe(cfg["root"] + "/led/set", 1)

        def disconnected(c, userdata, flags, reason, properties):
            if role == "cloud":
                self.cloud_up.clear()
            LOG.warning("%s terputus: %s", role, reason)

        def message(c, userdata, msg):
            try:
                self.inbox.put_nowait((role, msg.topic, msg.payload, msg.retain))
            except queue.Full:
                LOG.error("Antrean RAM penuh; pesan dibuang sebelum tersimpan")

        client.on_connect, client.on_disconnect, client.on_message = connected, disconnected, message
        return client

    def process(self, item):
        role, topic, payload, retained = item
        if role == "cloud":
            if retained or payload not in (b"on", b"off"):
                LOG.warning("Perintah cloud ditolak (retain/payload)")
                return
            if self.local.is_connected():
                self.local.publish(self.config["local"]["root"] + "/led/set",
                                   payload, qos=1, retain=False)
            return
        if topic == self.config["local"]["root"] + "/led/state":
            if payload in (b"on", b"off"):
                self.last_state, self.state_pending = payload, True
            return
        if retained:
            LOG.warning("Sensor retained dilewati agar tidak dianggap sampel baru")
            return
        try:
            data = validate(payload)
        except (ValueError, UnicodeDecodeError) as error:
            LOG.warning("Sensor ditolak: %s", error)
            return
        event_id = uuid.uuid4().hex
        stamp = datetime.now(timezone.utc).isoformat()
        data.update(event_id=event_id, received_at=stamp)
        self.db.execute("INSERT INTO samples(event_id,received_at,payload) VALUES(?,?,?)",
                        (event_id, stamp, json.dumps(data, allow_nan=False)))
        self.db.commit()
        LOG.info("Sampel tersimpan event_id=%s", event_id)

    def flush_one(self):
        if not self.cloud_up.is_set():
            return
        if self.state_pending and self.last_state is not None:
            state = self.cloud.publish(self.config["cloud"]["root"] + "/led/state",
                                       self.last_state, qos=1, retain=True)
            try:
                state.wait_for_publish(timeout=3)
                if state.is_published(): self.state_pending = False
            except (RuntimeError, ValueError):
                pass
        row = self.db.execute("SELECT event_id,payload FROM samples WHERE sent=0 ORDER BY rowid LIMIT 1").fetchone()
        if row is None:
            return
        info = self.cloud.publish(self.config["cloud"]["root"] + "/sensor",
                                  row[1], qos=1, retain=False)
        try:
            info.wait_for_publish(timeout=3)
            if info.is_published():
                self.db.execute("UPDATE samples SET sent=1 WHERE event_id=?", (row[0],))
                self.db.commit()
                LOG.info("Cloud PUBACK event_id=%s", row[0])
        except (RuntimeError, ValueError) as error:
            LOG.warning("Publish menunggu koneksi: %s", error)

    def run(self):
        for role in ("local", "cloud"):
            cfg = self.config[role]
            client = getattr(self, role)
            client.connect_async(cfg["host"], cfg["port"], 30)
            client.loop_start()
        try:
            while not self.stop.is_set():
                try:
                    self.process(self.inbox.get(timeout=0.2))
                except queue.Empty:
                    pass
                self.flush_one()
        finally:
            for client in (self.local, self.cloud):
                client.disconnect()
                client.loop_stop()
            self.db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        config_path = args.config.resolve()
        gateway = Gateway(json.loads(config_path.read_text(encoding="utf-8")), config_path.parent)
        signal.signal(signal.SIGINT, lambda *args: gateway.stop.set())
        signal.signal(signal.SIGTERM, lambda *args: gateway.stop.set())
        gateway.run()
    except (OSError, ValueError, KeyError) as error:
        LOG.error("Konfigurasi/koneksi gagal: %s", error)
        raise SystemExit(1)

"""MQTTS publish/subscribe probe. No insecure TLS option is provided."""
import argparse
import json
import ssl
import threading
import uuid
from pathlib import Path
import paho.mqtt.client as mqtt


def probe(host, port, ca, username=None, password=None, root=None):
    root = root or "unja/mk38/tls/" + uuid.uuid4().hex
    connected, received = threading.Event(), threading.Event()
    result = {"host": host, "port": port, "topic": root, "connack": None}
    payload = json.dumps({"uji": "TLS", "id": uuid.uuid4().hex})
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id="uji-" + uuid.uuid4().hex[:16])
    client.tls_set(ca_certs=str(ca), tls_version=ssl.PROTOCOL_TLS_CLIENT)
    if username is not None:
        client.username_pw_set(username, password)

    def on_connect(c, userdata, flags, reason, properties):
        result["connack"] = str(reason)
        if not reason.is_failure:
            c.subscribe(root, qos=1)
        connected.set()

    def on_subscribe(c, userdata, mid, reasons, properties):
        if all(not reason.is_failure for reason in reasons):
            c.publish(root, payload, qos=1, retain=False)

    def on_message(c, userdata, message):
        if message.topic == root and message.payload.decode() == payload:
            received.set()

    client.on_connect, client.on_subscribe = on_connect, on_subscribe
    client.on_message = on_message
    try:
        client.connect(host, port, keepalive=20)
        client.loop_start()
        connected.wait(12)
        if result["connack"] == "Success":
            received.wait(12)
        result["roundtrip"] = received.is_set()
    except (OSError, ssl.SSLError) as error:
        result.update(error=type(error).__name__ + ": " + str(error), roundtrip=False)
    finally:
        client.disconnect()
        client.loop_stop()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="broker.hivemq.com")
    parser.add_argument("--port", type=int, default=8883)
    parser.add_argument("--ca", type=Path, default=Path(__file__).with_name("amazon-root-ca1.pem"))
    parser.add_argument("--username")
    parser.add_argument("--password-env", default="MQTT_PASSWORD")
    parser.add_argument("--topic-root", default="unja/mk38/tls")
    args = parser.parse_args()
    import os
    outcome = probe(args.host, args.port, args.ca, args.username,
                    os.environ.get(args.password_env), args.topic_root + "/" + uuid.uuid4().hex)
    print(json.dumps(outcome, indent=2))
    raise SystemExit(0 if outcome["roundtrip"] else 1)

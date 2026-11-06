"""Generate disposable local TLS credentials, not production identities."""
import argparse
import base64
import datetime as dt
import hashlib
import ipaddress
import json
import os
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost", help="SAN hostname/IP for the local broker")
parser.add_argument("--out", type=Path, default=Path("runtime"))
parser.add_argument("--port", type=int, default=18883)
parser.add_argument("--listen", default="127.0.0.1")
parser.add_argument("--docker", action="store_true")
args = parser.parse_args()
password = os.environ.get("LOCAL_MQTT_PASSWORD")
if not password:
    raise SystemExit("Isi LOCAL_MQTT_PASSWORD sebelum membuat sertifikat dan password file.")
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
if (out / "server.key").exists():
    raise SystemExit("Sertifikat sudah ada; gunakan folder baru agar identitas tidak tertimpa.")
now = dt.datetime.now(dt.timezone.utc)
ca_key = rsa.generate_private_key(65537, 2048)
ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "MK38 local lab CA")])
ca = (x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name)
      .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
      .not_valid_before(now-dt.timedelta(minutes=5)).not_valid_after(now+dt.timedelta(days=30))
      .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
      .sign(ca_key, hashes.SHA256()))
server_key = rsa.generate_private_key(65537, 2048)
names = [x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
try:
    names.append(x509.IPAddress(ipaddress.ip_address(args.host)))
except ValueError:
    if args.host != "localhost": names.append(x509.DNSName(args.host))
server = (x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, args.host)]))
          .issuer_name(ca_name).public_key(server_key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now-dt.timedelta(minutes=5)).not_valid_after(now+dt.timedelta(days=30))
          .add_extension(x509.SubjectAlternativeName(names), critical=False)
          .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
          .sign(ca_key, hashes.SHA256()))
(out / "ca.crt").write_bytes(ca.public_bytes(serialization.Encoding.PEM))
(out / "server.crt").write_bytes(server.public_bytes(serialization.Encoding.PEM))
(out / "server.key").write_bytes(server_key.private_bytes(serialization.Encoding.PEM,
    serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))
# The CA private key is deliberately not saved.
salt = os.urandom(12)
digest = hashlib.pbkdf2_hmac("sha512", password.encode(), salt, 101)
encoded = "$7$101$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(digest).decode()
(out / "passwords").write_text("perangkat:" + encoded + "\n", encoding="ascii")
(out / "acl").write_text("user perangkat\ntopic readwrite unja/mk38/p14/#\n", encoding="ascii")
prefix = "/mosquitto/config" if args.docker else out.as_posix()
listener = "8883" if args.docker else f"{args.port} {args.listen}"
config = f"listener {listener}\nallow_anonymous false\npassword_file {prefix}/passwords\nacl_file {prefix}/acl\ncertfile {prefix}/server.crt\nkeyfile {prefix}/server.key\nlog_dest stdout\n"
(out / "mosquitto.conf").write_text(config, encoding="utf-8")
print(json.dumps({"folder": str(out), "san": args.host, "valid_days": 30, "username": "perangkat"}))

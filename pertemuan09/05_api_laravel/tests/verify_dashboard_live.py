"""Read existing simulator records through SQL, HTTP, and the browser CSV."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import urlparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--php', default='php')
parser.add_argument('--base-url', default='http://127.0.0.1:8000')
parser.add_argument('--device', default='esp32-kelompok-01')
parser.add_argument('--on-id', type=int, required=True)
parser.add_argument('--off-id', type=int, required=True)
args = parser.parse_args()
assert urlparse(args.base_url).hostname in ('127.0.0.1', 'localhost'), 'Local lab only.'


def get(path):
    with urlopen(args.base_url + path, timeout=8) as response:
        assert response.status == 200
        return json.load(response)


snapshot = json.loads(subprocess.run(
    [args.php, 'tests/inspect_database.php'], cwd=ROOT / 'backend',
    check=True, capture_output=True, encoding='utf-8',
).stdout)
assert snapshot['driver'] == 'mysql' and snapshot['database'] == 'mk38_sensor'
assert 'MariaDB' not in snapshot['server_version']
assert get('/api/v1/health') == {'status': 'ok'}
data = get('/api/v1/pemantauan?device_id=' + args.device + '&limit=100')
assert data['device']['device_id'] == args.device
assert data['device']['led'] is False
commands = {row['id']: row for row in snapshot['commands']}
http_commands = {row['id']: row for row in data['commands']}
observed = []
for command_id, led in ((args.on_id, True), (args.off_id, False)):
    row = commands[command_id]
    assert row['device_id'] == args.device and bool(row['led']) is led
    assert row['status'] == http_commands[command_id]['status'] == 'applied'
    assert row['acknowledged_at'] is not None
    created = datetime.fromisoformat(row['created_at'])
    acknowledged = datetime.fromisoformat(row['acknowledged_at'])
    observed.append(dict(id=command_id, led=led, status=row['status'],
                         created_at_utc=row['created_at'], acknowledged_at_utc=row['acknowledged_at'],
                         request_to_ack_seconds=(acknowledged - created).total_seconds()))
assert commands[args.on_id]['created_at'] < commands[args.off_id]['created_at']

ui = json.loads((ROOT / 'bukti/browser_dashboard_checks.json').read_text(encoding='utf-8'))
export = next(row for row in ui['checks'] if row.get('check') == 'csv_matches_paused_visible_table')
with (ROOT / 'bukti/dashboard_export.csv').open(encoding='utf-8-sig', newline='') as stream:
    rows = list(csv.DictReader(stream))
assert [row['id'] for row in rows] == export['csv_ids_ascending']
assert [row['id'] for row in reversed(rows)] == export['table_ids_descending']
for row in rows:
    api_row = get('/api/v1/sensor/' + row['id'])
    assert api_row['device_id'] == row['device_id'] == args.device
    assert api_row['suhu'] == float(row['suhu_celsius'])
    assert api_row['kelembapan'] == float(row['kelembapan_persen'])
assert data['latest']['suhu'] == 35 and data['latest']['kelembapan'] == 75
old_report = json.loads((ROOT / 'bukti/live_result.json').read_text(encoding='utf-8'))
for original in old_report['matched_examples']:
    assert get('/api/v1/sensor/' + str(original['id'])) == original

hashes = {}
for folder in ('backend/app', 'backend/routes', 'backend/database/migrations',
               'backend/resources/views', 'backend/public', 'backend/tests',
               'esp32/include', 'esp32/src', 'esp32/versi', 'tahapan'):
    for path in sorted((ROOT / folder).rglob('*')):
        if path.is_file():
            hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
for name in ('backend/composer.lock', 'backend/bootstrap/app.php', 'esp32/platformio.ini',
             'esp32/diagram.json', 'esp32/wokwi.toml'):
    hashes[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
report = dict(status='PASS', recorded_utc=datetime.now(timezone.utc).isoformat(),
    path='Browser button -> Laravel command -> Wokwi ESP32 GPIO -> confirmation -> MySQL -> HTTP/SQL check',
    database=snapshot, commands=observed, csv_rows_matched=len(rows), csv_href=export['href'],
    latest=data['latest'], online_at_check=data['online'], previous_samples_preserved=True,
    source_hashes=hashes,
    limits=['Request-to-ack times include simulator scheduling/startup and HTTP polling; no one-second guarantee.',
            'GPIO confirmation is firmware feedback, not a physical current measurement.',
            'Only the final control firmware was operated in this dashboard run; all four versions were compiled.',
            'Local HTTP without device authentication, TLS, MQTT, or physical hardware validation.'])
(ROOT / 'bukti/live_dashboard_result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(dict(status='PASS', database_version=snapshot['server_version'],
                     stored_sensor_rows=snapshot['count'], commands=observed,
                     csv_rows_matched=len(rows), previous_samples_preserved=True), indent=2))

"""Compare real HTTP reads with MySQL rows written by the simulator."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--php', default='php')
parser.add_argument('--base-url', default='http://127.0.0.1:8000')
parser.add_argument('--before-restart', type=Path, required=True)
args = parser.parse_args()


def get(path):
    with urlopen(args.base_url+path, timeout=5) as response:
        assert response.status == 200
        return json.load(response)


snapshot = json.loads(subprocess.run(
    [args.php, 'tests/inspect_database.php'], cwd=ROOT/'backend',
    check=True, capture_output=True, encoding='utf-8',
).stdout)
assert snapshot['driver'] == 'mysql'
assert 'MariaDB' not in snapshot['server_version']
assert snapshot['database'] == 'mk38_sensor'
assert get('/api/v1/health') == {'status': 'ok'}
expected = {(28.,65.),(32.,70.),(35.,75.)}
examples = {(float(r['suhu']),float(r['kelembapan'])):r for r in snapshot['examples']}
assert expected <= set(examples)
observed = []
for pair in sorted(expected):
    row = examples[pair]
    result = get('/api/v1/sensor/'+str(row['id']))
    assert (result['suhu'], result['kelembapan']) == pair
    assert result['device_id'] == 'esp32-kelompok-01'
    observed.append(result)
before = json.loads(args.before_restart.read_text(encoding='utf-8-sig'))
after = get('/api/v1/sensor/'+str(before['id']))
assert {k:v for k,v in after.items() if k != 'created_at'} == {k:v for k,v in before.items() if k != 'created_at'}
# PowerShell serializes a parsed ISO timestamp without its trailing zero microseconds.
assert datetime.fromisoformat(after['created_at'].replace('Z','+00:00')) == datetime.fromisoformat(before['created_at'].replace('Z','+00:00'))
hashes = {}
for base in (ROOT/'backend/app', ROOT/'backend/routes', ROOT/'backend/database/migrations',
             ROOT/'esp32/include', ROOT/'esp32/src', ROOT/'esp32/versi', ROOT/'tahapan'):
    for path in sorted(base.rglob('*')):
        if path.is_file():
            hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
for name in ('backend/composer.lock','backend/bootstrap/app.php','esp32/diagram.json','esp32/platformio.ini'):
    hashes[name] = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
report = dict(status='PASS', recorded_utc=datetime.now(timezone.utc).isoformat(),
    path='ESP32 DHT22 in Wokwi VS Code -> local Laravel API -> MySQL -> independent HTTP GET and SQL read',
    database=snapshot, matched_examples=observed,
    api_process_restart_preserved_record=True, before_restart=before,
    source_hashes=hashes,
    limits=['Local HTTP lab without device authentication; not deployed to the internet.',
            'The final sensor firmware ran in Wokwi. The first two firmware versions were compiled, not separately run in the simulator.',
            'A valid intermediate 32/65 sample was recorded while the two sliders were changed separately.'])
out = ROOT/'bukti'
out.mkdir(exist_ok=True)
(out/'live_result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(status='PASS',mysql_version=snapshot['server_version'],rows=snapshot['count'],
    matched_examples=observed,persistence_after_api_restart=True),indent=2))

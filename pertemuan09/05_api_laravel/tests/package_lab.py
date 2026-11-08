"""Package the lab only when current sources match the recorded test evidence."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

LAB = Path(__file__).resolve().parents[1]
MK38 = LAB.parent
REPO = MK38.parent


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


for filename in ('live_dashboard_result.json', 'laravel_dashboard_tests.json'):
    report = json.loads((LAB / 'bukti' / filename).read_text(encoding='utf-8'))
    assert report['status'] == 'PASS', filename
    for name, expected in report['source_hashes'].items():
        assert sha((LAB / name).read_bytes()) == expected, name

actuator = json.loads((LAB / 'bukti/aktuator_verifikasi.json').read_text(encoding='utf-8'))
assert actuator['status'] == 'PASS' and actuator['runtime_commands'] == 7 and actuator['firmware_versions'] == 3
for name, expected in actuator['source_hashes'].items():
    assert sha((LAB / name).read_bytes()) == expected, name
assert sha((LAB / 'bukti/actuators_live.json').read_bytes()) == actuator['runtime_report_sha256']
assert sha((LAB / 'bukti/actuators_ui.json').read_bytes()) == actuator['ui_report_sha256']
assert sha((LAB / 'bukti/actuator_firmware_builds.json').read_bytes()) == actuator['firmware_report_sha256']
for name, expected in actuator['python_http_reports'].items():
    assert sha((LAB / 'bukti' / name).read_bytes()) == expected, name
for name, expected in actuator['screenshots'].items():
    assert sha((LAB / 'bukti' / name).read_bytes()) == expected, name
tests = json.loads((LAB / 'bukti/laravel_dashboard_tests.json').read_text(encoding='utf-8'))
assert tests['suite']['tests'] == '12' and tests['suite']['assertions'] == '105'
assert all(tests['suite'][key] == '0' for key in ('errors', 'failures', 'skipped'))
firmware = json.loads((LAB / 'bukti/firmware_dashboard_builds.json').read_text(encoding='utf-8'))
assert firmware['status'] == 'PASS' and len(firmware['versions']) == 4
for item in firmware['versions']:
    assert sha((LAB / 'esp32/versi' / item['version']).read_bytes()) == item['source_sha256']
assert (LAB / 'esp32/src/main.cpp').read_bytes() == (LAB / 'esp32/versi/04_kendali.cpp').read_bytes()
assert (LAB / 'backend/routes/api.php').read_bytes() == (LAB / 'tahapan/04_api_dashboard.php').read_bytes()
assert (LAB / 'referensi/project_brief.tex').read_bytes() == (
    MK38 / 'source/assessments/final_project/project_brief.tex').read_bytes()
contrast = json.loads((LAB / 'bukti/dashboard_contrast.json').read_text(encoding='utf-8'))
assert contrast['status'] == 'PASS' and len(contrast['results']) == 22
audit = (LAB / 'AUDIT_DASHBOARD.md').read_text(encoding='utf-8')
assert 'FAIL' not in audit and all(f'R-{i:02d} PASS:' in audit for i in range(1, 41))

result = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard',
                         '--', 'modul_mk38/api_sensor'], cwd=REPO, check=True, capture_output=True)
paths = [REPO / name for name in sorted(set(result.stdout.decode('utf-8').strip('\0').split('\0')))]
assert paths and all(path.is_file() and path.is_relative_to(LAB) for path in paths)
assert LAB / 'backend/.env.example' in paths, 'Konfigurasi contoh wajib disertakan.'
excluded = {'vendor', 'node_modules', '.pio', '.venv', '__pycache__'}
assert all(not excluded.intersection(path.relative_to(LAB).parts) for path in paths)
assert all(path.relative_to(LAB).parts[0] not in ('build', 'data') for path in paths)
assert all(path.name == '.gitignore' for path in paths if 'storage' in path.relative_to(LAB).parts)
assert all(path.name not in ('.env', '.env.testing') for path in paths)
private = []
for name in ('.env', '.env.testing'):
    env = LAB / 'backend' / name
    if env.exists():
        private.extend(value.strip().strip('"\'') for key, value in
                       re.findall(r'^(APP_KEY|DB_PASSWORD)=(.*)$', env.read_text(), re.M) if value.strip())
manifest = {}
for path in paths:
    payload = path.read_bytes()
    assert all(value.encode() not in payload for value in private), path.name
    if path.suffix in ('.md', '.js', '.css', '.php') and 'referensi' not in path.relative_to(LAB).parts:
        assert '\u2014' not in payload.decode('utf-8'), path.name
    manifest[path.relative_to(LAB).as_posix()] = sha(payload)
output = MK38 / 'dist/api_sensor_laravel_mysql.zip'
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as bundle:
    for path in paths:
        bundle.write(path, 'api_sensor/' + path.relative_to(LAB).as_posix())
    bundle.writestr('api_sensor/MANIFEST_SHA256.json', json.dumps(manifest, indent=2))
with zipfile.ZipFile(output) as bundle:
    assert bundle.testzip() is None
    for name, expected in manifest.items():
        assert sha(bundle.read('api_sensor/' + name)) == expected, name
print(json.dumps(dict(status='PASS', files=len(paths), bytes=output.stat().st_size,
                     tests=12, assertions=105, firmware_versions=4,
                     zip_sha256=sha(output.read_bytes()), archive=str(output)), indent=2))

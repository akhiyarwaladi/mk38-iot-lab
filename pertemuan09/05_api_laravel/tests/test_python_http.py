"""Exercise the teaching clients through real Laravel/MySQL, then real Wokwi.

Developer verification only: pymysql is used for an independent SQL check.
The distributed teaching clients themselves use only the standard library.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pymysql

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
WORK = ROOT/'build/python HTTP clients'
FRESH = ROOT/'build/online_lab/fresh student checkout/pertemuan09/05_api_laravel'
PHP = 'C:/xampp/php/php.exe'
CNF = ROOT/'build/laravel_api_20261106/client.local.cnf'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
RUN = uuid.uuid4().hex[:8]
SENSOR_TEST = 'python-http-sensor-' + RUN
ACTUATOR_TEST = 'python-http-actuator-' + RUN


def connection(database):
    assert CNF.is_file(), 'Local MySQL verification config is missing.'
    return pymysql.connect(read_default_file=str(CNF), database=database,
                           autocommit=True, cursorclass=pymysql.cursors.DictCursor)


def query(db, sql, params=()):
    with db.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def prepare(name, url, sensor, actuator):
    folder = WORK/name/'client_python'
    folder.mkdir(parents=True, exist_ok=True)
    for path in (LAB/'client_python').glob('*.py'):
        shutil.copyfile(path, folder/path.name)
    (folder/'konfigurasi.py').write_text(
        f'API_DASAR = {url!r}\nID_SENSOR = {sensor!r}\nID_AKTUATOR = {actuator!r}\n', encoding='utf-8')
    return folder


def run(folder, name, change=None, expected=0):
    path = folder/name
    original = path.read_bytes()
    if change:
        text = original.decode('utf-8')
        assert change[0] in text, (name, change)
        path.write_text(text.replace(*change), encoding='utf-8')
    try:
        result = subprocess.run([sys.executable, '-B', str(path)], cwd=folder.parent,
            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=35)
        assert result.returncode == expected, (name, result.stdout, result.stderr)
        assert 'Traceback' not in result.stdout + result.stderr
        return {'script': name, 'change': change, 'exit_code': result.returncode,
                'stdout': result.stdout, 'stderr': result.stderr}
    finally:
        path.write_bytes(original)


def staged():
    folder = prepare('staged', 'http://127.0.0.1:8019', SENSOR_TEST, ACTUATOR_TEST)
    backend = FRESH/'backend'
    routes = backend/'routes/api.php'
    original = routes.read_bytes()
    cases = []
    db = connection('mk38_sensor_test')
    for table in ('sensors', 'devices'):
        assert not query(db, f'SELECT * FROM {table} WHERE device_id=%s', (SENSOR_TEST,))
    log = (WORK/'staged-server.log').open('w', encoding='utf-8')
    server = subprocess.Popen([PHP, '-S', '127.0.0.1:8019', '-t', str(backend/'public'),
        str(backend/'vendor/laravel/framework/src/Illuminate/Foundation/resources/server.php')],
        cwd=backend/'public', stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
    def stage(name): shutil.copyfile(FRESH/'tahapan'/name, routes)
    try:
        stage('01_api_health.php')
        for _ in range(50):
            try:
                with urlopen('http://127.0.0.1:8019/api/v1/health', timeout=1) as response:
                    if response.status == 200: break
            except (URLError, TimeoutError): time.sleep(.2)
        else: raise AssertionError('Isolated Laravel server unavailable')
        cases.append(run(folder, '01_health.py'))
        stage('02_api_terima.php')
        for change, status in [(None, 200), (('"kelembapan": 65.0', '"kelembapan": 101.0'), 422), (None, 200)]:
            item = run(folder, '02_kirim_sensor.py', change, int(status >= 400))
            assert f'HTTP {status}' in item['stdout']
            assert not query(db, 'SELECT id FROM sensors WHERE device_id=%s', (SENSOR_TEST,))
            item['mysql_sensor_rows'] = 0
            cases.append(item)
        stage('03_api_mysql.php')
        cases.append(run(folder, '03_simpan_baca.py'))
        rows = query(db, 'SELECT id,device_id,suhu,kelembapan FROM sensors WHERE device_id=%s', (SENSOR_TEST,))
        assert len(rows) == 1 and float(rows[0]['suhu']) == 28 and float(rows[0]['kelembapan']) == 65
        cases[-1]['sql_record'] = {k: str(v) for k, v in rows[0].items()}
        cases.append(run(folder, '04_baca_sensor.py'))
        stage('04_api_dashboard.php')
        for change in (None, ('NILAI_LED = True', 'NILAI_LED = False')):
            cases.append(run(folder, '05_perintah_led.py', change))
        for name in ('06_daftar_led.py', '06_daftar_led.py', '07_daftar_servo.py'):
            cases.append(run(folder, name))
        actuators = query(db, 'SELECT id,name,reported_value FROM actuators WHERE device_id=%s ORDER BY id', (ACTUATOR_TEST,))
        assert len(actuators) == 2 and all(row['reported_value'] is None for row in actuators)
        assert not query(db, 'SELECT id FROM sensors WHERE device_id=%s', (ACTUATOR_TEST,))
        cases.append(run(folder, '08_target_led.py'))
        cases.append(run(folder, '09_baca_aktuator.py'))
        lamp = next(row['id'] for row in actuators if row['name'] == 'lampu')
        row = query(db, 'SELECT requested_value,reported_value FROM actuators WHERE id=%s', (lamp,))[0]
        assert row == {'requested_value': 1, 'reported_value': None}
        for change in (None, ('SUDUT = 90', 'SUDUT = 0'), ('SUDUT = 90', 'SUDUT = 180')):
            cases.append(run(folder, '10_servo.py', change))
        before = query(db, 'SELECT COUNT(*) AS n FROM actuator_commands')[0]['n']
        cases.append(run(folder, '11_uji_servo_salah.py'))
        assert query(db, 'SELECT COUNT(*) AS n FROM actuator_commands')[0]['n'] == before
        time.sleep(31)
        cases.append(run(folder, '09_baca_aktuator.py'))
        assert query(db, 'SELECT status FROM actuator_commands WHERE actuator_id=%s ORDER BY id DESC LIMIT 1', (lamp,))[0]['status'] == 'expired'
        # Exercise the shared helper against a real Laravel 404 JSON response.
        result = subprocess.run([sys.executable, '-B', '-c',
            "from http_json import minta; status,data=minta('GET','/api/v1/tidak-ada'); assert status==404"],
            cwd=folder, capture_output=True, text=True, encoding='utf-8', timeout=20)
        assert result.returncode == 0 and 'HTTP 404' in result.stdout
        cases.append({'script': 'http_json.py', 'case': 'Laravel 404', 'stdout': result.stdout})
    finally:
        server.terminate(); server.wait(timeout=10); log.close()
        routes.write_bytes(original); db.close()
    cases.append(run(folder, '01_health.py', expected=1))
    cases.append(run(folder, '02_kirim_sensor.py', expected=1))
    cases.append(run(folder, '04_baca_sensor.py', expected=1))
    return cases


def live():
    folder = prepare('live', 'http://127.0.0.1:8000', 'esp32-kelompok-01', 'esp32-aktuator-01')
    db = connection('mk38_sensor')
    cases = []
    try:
        rows = query(db, 'SELECT id,name,reported_at,boot_id FROM actuators WHERE device_id=%s', ('esp32-aktuator-01',))
        assert len(rows) == 2 and all(row['boot_id'] for row in rows)
        for name, change, output, value in [
            ('08_target_led.py', None, 'lampu', 1),
            ('10_servo.py', ('SUDUT = 90', 'SUDUT = 0'), 'pintu', 0),
            ('10_servo.py', None, 'pintu', 90),
            ('10_servo.py', ('SUDUT = 90', 'SUDUT = 180'), 'pintu', 180),
            ('10_servo.py', ('SUDUT = 90', 'SUDUT = 0'), 'pintu', 0),
            ('08_target_led.py', ('NILAI = 1', 'NILAI = 0'), 'lampu', 0)]:
            item = run(folder, name, change)
            actuator = next(row['id'] for row in rows if row['name'] == output)
            command = query(db, 'SELECT id,value FROM actuator_commands WHERE actuator_id=%s ORDER BY id DESC LIMIT 1', (actuator,))[0]
            assert command['value'] == value
            for _ in range(60):
                result = query(db, 'SELECT c.id,c.status,c.acknowledged_at,a.reported_value,a.boot_id,e.id AS event_id,e.value AS event_value FROM actuator_commands c JOIN actuators a ON a.id=c.actuator_id LEFT JOIN actuator_state_events e ON e.command_id=c.id WHERE c.id=%s', (command['id'],))[0]
                if result['status'] == 'applied': break
                time.sleep(.25)
            else: raise AssertionError(('No real firmware acknowledgement', command['id'], result['status']))
            assert result['reported_value'] == value and result['event_value'] == value and result['event_id'] and result['acknowledged_at']
            item['sql_firmware_confirmation'] = {k: str(v) for k, v in result.items()}
            cases.append(item)
        cases.append(run(folder, '11_uji_servo_salah.py'))
        cases.append(run(folder, '09_baca_aktuator.py'))
    finally: db.close()
    return cases


if __name__ == '__main__':
    phase = sys.argv[1]
    assert phase in ('staged', 'live')
    WORK.mkdir(parents=True, exist_ok=True)
    cases = staged() if phase == 'staged' else live()
    report = {'status': 'PASS', 'phase': phase, 'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'python': sys.version.split()[0], 'platform': sys.platform,
        'source_hashes': {p.relative_to(LAB).as_posix(): sha(p) for p in sorted((LAB/'client_python').glob('*.py'))},
        'cases': cases, 'scope': 'Real Laravel and MySQL; HTTP-only synthetic sensor input' if phase == 'staged' else
            'Python sends commands; real ESP32 Wokwi firmware supplies acknowledgements; independent SQL checks; no simulated acknowledgements',
        'limits': ['Windows runtime tested; Linux/macOS not executed.', 'Servo reports PWM setting; no mechanical position sensor or physical hardware.']}
    (LAB/'bukti'/f'python_http_{phase}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'phase': phase, 'cases': len(cases)}, indent=2))

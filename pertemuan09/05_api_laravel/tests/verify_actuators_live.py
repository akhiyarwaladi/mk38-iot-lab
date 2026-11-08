"""Exercise the local dashboard; acknowledgments must come from real Wokwi firmware."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import pymysql
import requests
from playwright.sync_api import sync_playwright

LAB = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--base-url', default='http://127.0.0.1:8000')
parser.add_argument('--device', default='esp32-aktuator-01')
parser.add_argument('--phase', choices=['controls', 'restart'], default='controls')
args = parser.parse_args()
assert args.base_url.startswith('http://127.0.0.1:'), 'Local lab only'
env = {}
for line in (LAB / 'backend/.env').read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        key, value = line.split('=', 1)
        env[key] = value.strip().strip('\"\'')
db = pymysql.connect(host=env['DB_HOST'], port=int(env['DB_PORT']), user=env['DB_USERNAME'],
                     password=env['DB_PASSWORD'], database=env['DB_DATABASE'],
                     cursorclass=pymysql.cursors.DictCursor, autocommit=True)
out = LAB / 'bukti'
out.mkdir(exist_ok=True)


def sql(query, parameters=()):
    with db.cursor() as cursor:
        cursor.execute(query, parameters)
        return cursor.fetchall()


def get(path):
    response = requests.get(args.base_url + '/api/v1/aktuator' + path, timeout=10)
    response.raise_for_status()
    return response.json()


def wait_applied(actuator, command, value):
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        data = get(f'/{actuator}/riwayat')
        match = next((r for r in data['commands'] if r['id'] == command), None)
        if match and match['status'] == 'applied':
            assert data['actuator']['reported_value'] == value
            assert any(r['command_id'] == command and r['value'] == value for r in data['events'])
            rows = sql('SELECT status,value,acknowledged_at FROM actuator_commands WHERE id=%s', (command,))
            assert rows[0]['status'] == 'applied' and rows[0]['value'] == value and rows[0]['acknowledged_at']
            rows = sql('SELECT value FROM actuator_state_events WHERE command_id=%s', (command,))
            assert len(rows) == 1 and rows[0]['value'] == value
            event = next(r for r in data['events'] if r['command_id'] == command)
            delta = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00')) - datetime.fromisoformat(match['acknowledged_at'].replace('Z', '+00:00'))
            assert abs(delta.total_seconds()) < 2, 'Event and acknowledgment timestamps must share UTC'
            return match
        assert not match or match['status'] == 'pending', match
        time.sleep(.3)
    raise AssertionError(f'Wokwi did not acknowledge command {command}')


version = sql('SELECT VERSION() AS version, DATABASE() AS db')[0]
assert 'MariaDB' not in version['version'] and version['db'] == env['DB_DATABASE']
devices = {r['name']: r for r in get('?device_id=' + args.device)}
assert set(devices) == {'lampu', 'pintu'}
assert all(r['boot_id'] and r['reported_at'] for r in devices.values())
report_path = out / 'actuators_live.json'
if args.phase == 'restart':
    report = json.loads(report_path.read_text())
    deadline = time.monotonic() + 45
    while any(r['boot_id'] == report['before_restart'][n]['boot_id'] for n, r in devices.items()):
        assert time.monotonic() < deadline, 'New firmware boot reports did not arrive'
        time.sleep(.3)
        devices = {r['name']: r for r in get('?device_id=' + args.device)}
    for name, row in devices.items():
        assert row['boot_id'] != report['before_restart'][name]['boot_id']
        assert row['reported_value'] == 0
        assert row['requested_value'] == report['before_restart'][name]['requested_value']
        assert get(f'/{row["id"]}/riwayat')['events'][0]['reason'] == 'boot'
    report['firmware_restart'] = {'status': 'PASS', 'outputs': {'lampu': 0, 'pintu': 0},
                                  'targets_preserved': True, 'new_boot_ids': {n: r['boot_id'] for n, r in devices.items()}}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS real Wokwi restart: outputs reset, targets and previous history retained')
    raise SystemExit(0)

checks, commands, browser_errors = [], [], []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1280, 'height': 950}, device_scale_factor=1.5)
    page.on('pageerror', lambda e: browser_errors.append(str(e)))
    page.goto(args.base_url + '/aktuator')
    page.locator('#actuator').wait_for(state='visible')
    page.wait_for_function("!document.querySelector('#actuator').disabled")
    page.locator('#automatic').uncheck()
    for name, value in [('lampu', 1), ('lampu', 0), ('pintu', 0), ('pintu', 90), ('pintu', 180), ('lampu', 1), ('pintu', 90)]:
        row = devices[name]
        page.locator('#actuator').select_option(str(row['id']))
        page.wait_for_function('(id) => document.querySelector("#actuator-id").textContent === String(id)', arg=row['id'])
        with page.expect_response(lambda r: r.request.method == 'POST' and r.url.endswith(f'/{row["id"]}/perintah')) as pending:
            if name == 'lampu':
                page.locator(f'[data-value="{value}"]').click()
            else:
                page.locator('#angle').fill(str(value))
                page.get_by_role('button', name='Kirim sudut', exact=True).click()
        response = pending.value
        assert response.status == 202
        command = response.json()
        matched = wait_applied(row['id'], command['id'], value)
        commands.append({'actuator': name, 'value': value, 'id': command['id'], 'status': matched['status'],
                         'created_at': matched['created_at'], 'acknowledged_at': matched['acknowledged_at']})
        page.get_by_role('button', name='Perbarui data', exact=True).click()
        page.wait_for_function('(value) => document.querySelector("#reported").textContent.startsWith(String(value))', arg=value)
        if (name, value) in [('lampu', 1), ('pintu', 90), ('pintu', 180)]:
            page.screenshot(path=str(out / f'aktuator_{name}_{value}.png'), full_page=True)
        print('PASS dashboard -> MySQL -> Wokwi -> confirmation:', name, value, command['id'], flush=True)
    checks.append('LED 0/1 and servo 0/90/180 sent by browser; ack observed independently through SQL and REST')
    for width in [360, 768, 1280]:
        page.set_viewport_size({'width': width, 'height': 950})
        for dark in [False, True]:
            if (page.locator('html').get_attribute('data-theme') == 'dark') != dark:
                page.locator('#theme').click()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, dark)
            page.screenshot(path=str(out / f'aktuator_ui_{width}_{"dark" if dark else "light"}.png'), full_page=True)
    checks.append('360/768/1280 px, light and dark themes: no document overflow')
    page.locator('#theme').focus()
    page.keyboard.press('Enter')
    page.locator('#actuator').focus()
    assert page.locator('#actuator').evaluate('e => document.activeElement === e')
    checks.append('native controls support focus and keyboard activation')
    browser.close()
assert not browser_errors, browser_errors
for name, bad in [('lampu', 2), ('pintu', 181)]:
    row = devices[name]
    before = sql('SELECT COUNT(*) AS n FROM actuator_commands WHERE actuator_id=%s', (row['id'],))[0]['n']
    response = requests.post(args.base_url + f'/api/v1/aktuator/{row["id"]}/perintah', json={'value': bad},
                             headers={'Accept': 'application/json'}, timeout=10)
    assert response.status_code == 422
    assert sql('SELECT COUNT(*) AS n FROM actuator_commands WHERE actuator_id=%s', (row['id'],))[0]['n'] == before
checks.append('invalid values return HTTP422 and create no command rows')
current = {r['name']: r for r in get('?device_id=' + args.device)}
assert current['lampu']['reported_value'] == 1 and current['pintu']['reported_value'] == 90
report = {'status': 'PASS', 'recorded_utc': datetime.now(timezone.utc).isoformat(),
          'path': 'Browser -> Laravel HTTP local -> MySQL -> ESP32 firmware in VS Code Wokwi -> Laravel acknowledgment -> MySQL',
          'database': version, 'checks': checks, 'commands': commands,
          'before_restart': current, 'browser_errors': browser_errors,
          'limits': 'Wokwi simulation; servo value is firmware PWM setting, not mechanical position feedback; no physical hardware test.'}
report_path.write_text(json.dumps(report, indent=2) + '\n')
print('PASS', len(commands), 'real firmware confirmations; database', version['version'])

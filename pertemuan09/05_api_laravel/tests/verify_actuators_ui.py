"""Check local UI controls and explicitly injected empty/network error states."""
import json
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright, expect

OUT = Path(__file__).resolve().parents[1] / 'bukti'
checks, errors = [], []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':390,'height':850})
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto('http://127.0.0.1:8000/aktuator')
    page.wait_for_function("!document.querySelector('#actuator').disabled")
    servo = next(r for r in requests.get('http://127.0.0.1:8000/api/v1/aktuator?device_id=esp32-aktuator-01').json() if r['name'] == 'pintu')
    page.locator('#actuator').select_option(str(servo['id']))
    page.wait_for_function('(id) => document.querySelector("#actuator-id").textContent===String(id)', arg=servo['id'])
    page.locator('#automatic').uncheck()
    expect(page.locator('#refresh')).to_be_enabled()
    calls = []
    page.on('request', lambda r: calls.append(r.url) if '/api/v1/aktuator' in r.url else None)
    page.wait_for_timeout(2300)
    assert not calls, 'Pause must stop automatic HTTP reads'
    page.locator('#automatic').check()
    page.wait_for_timeout(2300)
    assert calls, 'Resume must restart HTTP reads'
    checks.append('Automatic refresh pauses and resumes HTTP reads')
    page.locator('#automatic').uncheck()
    expect(page.locator('#refresh')).to_be_enabled()
    page.locator('#angle').fill('181')
    assert page.locator('#angle').evaluate('e=>!e.checkValidity()')
    checks.append('Native servo form rejects 181 before POST')
    page.locator('#angle').fill('90')
    page.route('**/api/v1/aktuator*', lambda route: route.abort())
    page.locator('#refresh').click()
    expect(page.locator('#connection')).to_have_class('notice error')
    expect(page.locator('#servo-controls button')).to_be_disabled()
    assert 'sebelumnya' in page.locator('#connection').inner_text()
    checks.append('Network error labels retained data and disables command controls')
    page.unroute('**/api/v1/aktuator*')
    page.locator('#refresh').click()
    expect(page.locator('#servo-controls button')).to_be_enabled()
    checks.append('Manual retry recovers command controls')
    for path in ['/dashboard', '/latihan/tabel']:
        assert page.request.get('http://127.0.0.1:8000'+path).status == 200
    checks.append('Both navigation destinations return 200')
    empty = browser.new_page(viewport={'width':360,'height':850})
    empty.route('**/api/v1/aktuator', lambda route: route.fulfill(json=[]))
    empty.goto('http://127.0.0.1:8000/aktuator')
    expect(empty.locator('#connection')).to_contain_text('Belum ada aktuator')
    expect(empty.locator('#actuator')).to_be_disabled()
    expect(empty.locator('#servo-controls')).not_to_be_visible()
    expect(empty.locator('#led-controls')).not_to_be_visible()
    checks.append('Empty state explains registration and hides unavailable controls')
    assert not errors
    browser.close()
(OUT/'actuators_ui.json').write_text(json.dumps({'status':'PASS','checks':checks,'page_errors':errors,
    'scope':'Local browser UI; injected empty/network states are separate from real Wokwi control proof.'},indent=2)+'\n')
print('PASS',len(checks),'UI state and control checks')

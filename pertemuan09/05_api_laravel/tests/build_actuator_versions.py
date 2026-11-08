"""Compile all three actuator lessons; keep the active source intact."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

LAB = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--pio', required=True)
args = parser.parse_args()
project = LAB / 'esp32_aktuator'
work = LAB.parent / 'build/actuators_20261108/firmware'
(work/'src').mkdir(parents=True, exist_ok=True)
shutil.copyfile(project/'platformio.ini', work/'platformio.ini')
shutil.copytree(project/'include', work/'include', dirs_exist_ok=True)
results = []
for version in sorted((project/'versi').glob('*.cpp')):
    shutil.copyfile(version, work/'src/main.cpp')
    result = subprocess.run([args.pio, 'run', '-d', str(work)], capture_output=True,
                            encoding='utf-8', errors='replace', timeout=240)
    (work/(version.stem+'.log')).write_text(result.stdout+result.stderr, encoding='utf-8')
    assert result.returncode == 0, 'Inspect build log for ' + version.name
    results.append({'version':version.name,'status':'PASS',
        'source_sha256':hashlib.sha256(version.read_bytes()).hexdigest(),
        'firmware_sha256':hashlib.sha256((work/'.pio/build/esp32dev/firmware.bin').read_bytes()).hexdigest()})
    print('PASS build',version.name,flush=True)
assert (project/'src/main.cpp').read_bytes()==(project/'versi/03_led_servo_rest.cpp').read_bytes()
(LAB/'bukti/actuator_firmware_builds.json').write_text(json.dumps({'status':'PASS',
    'scope':'Compilation of all three teaching versions; simulator proof recorded separately.',
    'versions':results},indent=2)+'\n')

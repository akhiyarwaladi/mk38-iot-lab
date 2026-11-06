"""Compile each firmware version in a separate build directory."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--pio', default=shutil.which('pio'))
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if not args.pio:
    raise SystemExit('Berikan --pio dengan lokasi program PlatformIO.')
args.output.mkdir(parents=True, exist_ok=True)


def build(version):
    work = Path(tempfile.mkdtemp(prefix='mk38-'+version.stem+'-'))
    (work/'src').mkdir()
    shutil.copy2(ROOT/'esp32/platformio.ini', work/'platformio.ini')
    shutil.copytree(ROOT/'esp32/include', work/'include')
    shutil.copy2(version, work/'src/main.cpp')
    result = subprocess.run([args.pio, 'run', '-d', str(work)], capture_output=True,
                            encoding='utf-8', errors='replace', timeout=180)
    (args.output/(version.stem+'.log')).write_text(result.stdout+result.stderr, encoding='utf-8')
    assert result.returncode == 0, version.name
    firmware = work/'.pio/build/esp32dev/firmware.bin'
    return dict(version=version.name, status='PASS',
                source_sha256=hashlib.sha256(version.read_bytes()).hexdigest(),
                firmware_sha256=hashlib.sha256(firmware.read_bytes()).hexdigest())


with ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(build, sorted((ROOT/'esp32/versi').glob('*.cpp'))))
report = dict(status='PASS', scope='Compilation only; simulator evidence is recorded separately.', versions=results)
(args.output/'firmware_builds.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))

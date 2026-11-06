"""Tahap kedua: periksa status CSV dan berkas bukti lokal."""
import argparse
import csv
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("folder", type=Path)
args = parser.parse_args()
folder = args.folder.resolve()
errors = []
try:
    with (folder / "hasil_uji.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        errors.append("CSV belum berisi pengujian.")
    for number, row in enumerate(rows, 2):
        if row.get("status") not in {"LULUS", "GAGAL", "TIDAK_BERLAKU"}:
            errors.append(f"Baris {number}: putuskan status setelah menguji.")
        if not (row.get("hasil_aktual") or "").strip():
            errors.append(f"Baris {number}: hasil aktual belum diisi.")
        name = row.get("bukti") or ""
        target = (folder / name).resolve()
        if not name or not target.is_relative_to(folder) or not target.is_file():
            errors.append(f"Baris {number}: bukti tidak ditemukan/di luar folder.")
except OSError as error:
    errors.append(str(error))
print("\n".join(errors) if errors else "CSV dan lokasi bukti tersedia; kebenaran bukti belum dinilai.")
raise SystemExit(1 if errors else 0)

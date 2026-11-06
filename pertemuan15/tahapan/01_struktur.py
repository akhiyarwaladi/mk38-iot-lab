"""Tahap pertama: periksa nama berkas dan folder, tanpa membaca isinya."""
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("folder", type=Path)
args = parser.parse_args()
errors = []
for name in ("README.md", "project.json", "hasil_uji.csv", "laporan.pdf", "presentasi.pdf"):
    if not (args.folder / name).is_file():
        errors.append("Berkas belum ada: " + name)
for name in ("firmware", "desain", "bukti"):
    if not (args.folder / name).is_dir():
        errors.append("Folder belum ada: " + name)
print("\n".join(errors) if errors else "Struktur tersedia; isi belum diperiksa.")
raise SystemExit(1 if errors else 0)

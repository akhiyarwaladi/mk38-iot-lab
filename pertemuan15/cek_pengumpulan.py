"""Validate a project hand-in without executing student code or assigning grades."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import zipfile

REQUIRED = ("README.md", "laporan.pdf", "presentasi.pdf", "project.json", "hasil_uji.csv")
EXCLUDE = {".git", ".pio", "node_modules", ".venv", "__pycache__"}
PRIVATE_NAMES = {"secrets.h", ".env", "server.key", "passwords", "config.json"}


def inspect(folder):
    errors, files = [], []
    for name in REQUIRED:
        if not (folder / name).is_file(): errors.append("Berkas wajib belum ada: " + name)
    for dirname in ("firmware", "desain", "bukti"):
        if not (folder / dirname).is_dir(): errors.append("Folder wajib belum ada: " + dirname)
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder)
        if any(part in EXCLUDE for part in rel.parts): continue
        if path.is_symlink():
            errors.append("Symlink tidak diizinkan: " + rel.as_posix()); continue
        if not path.is_file(): continue
        if path.name in PRIVATE_NAMES:
            errors.append("Pindahkan berkas privat: " + rel.as_posix()); continue
        if path.suffix.lower() in {".h", ".cpp", ".py", ".js", ".json", ".md", ".txt", ".pem"}:
            content = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", content):
                errors.append("Private key terdeteksi: " + rel.as_posix())
        files.append(path)
    if (folder / "project.json").exists():
        try:
            data = json.loads((folder / "project.json").read_text(encoding="utf-8"))
            if not isinstance(data, dict): raise ValueError("root harus berupa object")
            for name in ("kelompok", "judul", "versi", "lingkungan", "anggota"):
                if not data.get(name) or data[name] == "ISI": errors.append("Isi project.json: " + name)
            if not isinstance(data.get("anggota"), list): errors.append("anggota harus berupa array")
        except (ValueError, OSError) as error: errors.append("project.json tidak valid: " + str(error))
    if (folder / "hasil_uji.csv").exists():
        try:
            with (folder / "hasil_uji.csv").open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            if not rows: errors.append("hasil_uji.csv kosong")
            for number, row in enumerate(rows, 2):
                if row.get("status") not in {"LULUS", "GAGAL", "TIDAK_BERLAKU"}:
                    errors.append(f"Baris {number}: status belum diputuskan")
                if not (row.get("hasil_aktual") or "").strip(): errors.append(f"Baris {number}: hasil aktual kosong")
                evidence = row.get("bukti") or ""
                target = (folder / evidence).resolve()
                if not evidence or not target.is_relative_to(folder.resolve()) or not target.is_file():
                    errors.append(f"Baris {number}: bukti lokal tidak ditemukan/di luar folder")
        except (ValueError, OSError) as error: errors.append("CSV tidak valid: " + str(error))
    return errors, files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--zip", type=Path)
    args = parser.parse_args()
    folder = args.folder.resolve()
    if not folder.is_dir(): raise SystemExit("Folder pengumpulan tidak ditemukan.")
    if args.zip and args.zip.resolve().is_relative_to(folder):
        raise SystemExit("Simpan ZIP di luar folder pengumpulan.")
    errors, files = inspect(folder)
    print(json.dumps({"siap_diperiksa": not errors, "errors": errors, "jumlah_berkas": len(files)}, indent=2))
    if errors: return 1
    if args.zip:
        manifest = {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        with zipfile.ZipFile(args.zip, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in files: archive.write(path, path.relative_to(folder).as_posix())
            archive.writestr("MANIFEST_SHA256.json", json.dumps(manifest, indent=2))
        print("ZIP tersimpan: " + str(args.zip.resolve()))
    return 0


if __name__ == "__main__": raise SystemExit(main())

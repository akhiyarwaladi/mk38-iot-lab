"""Summarize measured trials without assigning a project grade."""
import argparse
import csv
import json
import math
from pathlib import Path
import statistics


def angka(value, nama):
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(nama + ' harus berupa angka') from error
    if not math.isfinite(number) or number < 0:
        raise ValueError(nama + ' harus finite dan tidak negatif')
    return number


def baca(path, fields):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not set(fields) <= set(reader.fieldnames or []):
            raise ValueError('Kolom wajib: ' + ', '.join(fields))
        rows = list(reader)
    if not rows:
        raise ValueError('CSV belum berisi percobaan')
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError('Jumlah kolom setiap baris harus sesuai header')
    ids = [row.get('id') for row in rows]
    if any(not value or not value.strip() for value in ids) or len(set(ids)) != len(ids):
        raise ValueError('ID percobaan wajib terisi dan unik')
    environments = {row.get('lingkungan') for row in rows}
    if len(environments) != 1 or not environments <= {'SINTETIS', 'SIMULASI', 'HARDWARE'}:
        raise ValueError('Pisahkan lingkungan SINTETIS, SIMULASI, dan HARDWARE')
    return rows, environments.pop()


def hitung(mode, path, batas_ms=None):
    fields = {'klasifikasi': ['acuan', 'hasil'], 'latensi': ['status', 'durasi_ms'],
              'perbandingan': ['tetap_ms', 'adaptif_ms']}[mode]
    rows, environment = baca(path, ['id', 'lingkungan'] + fields)
    result = dict(metrik=mode, lingkungan=environment, percobaan=len(rows))
    if mode == 'klasifikasi':
        if any(not row.get('acuan') or not row.get('hasil') for row in rows):
            raise ValueError('Label acuan/hasil wajib terisi; gunakan TIDAK_TERBACA jika gagal membaca')
        correct = sum(row['acuan'] == row['hasil'] for row in rows)
        result.update(cocok=correct, tidak_cocok=len(rows) - correct, akurasi_persen=100 * correct / len(rows))
    elif mode == 'latensi':
        limit = angka(batas_ms, 'batas-ms')
        if limit == 0:
            raise ValueError('batas-ms harus lebih besar dari nol')
        if any(row.get('status') not in {'LULUS', 'GAGAL', 'TIMEOUT'} for row in rows):
            raise ValueError('Status harus LULUS, GAGAL, atau TIMEOUT')
        times = sorted(angka(row.get('durasi_ms'), 'durasi_ms') for row in rows if row['status'] == 'LULUS')
        within = sum(value <= limit for value in times)
        result.update(respons_berhasil=len(times), gagal_atau_timeout=len(rows) - len(times),
                      batas_ms=limit, berhasil_dalam_batas=within,
                      seluruh_percobaan_dalam_batas_persen=100 * within / len(rows),
                      rata_rata_ms=statistics.mean(times) if times else None,
                      maksimum_ms=max(times) if times else None,
                      p95_ms=times[math.ceil(.95 * len(times)) - 1] if times else None,
                      metode_p95='nearest rank; hanya respons LULUS, kegagalan tetap dihitung terpisah')
    else:
        fixed = [angka(row.get('tetap_ms'), 'tetap_ms') for row in rows]
        adaptive = [angka(row.get('adaptif_ms'), 'adaptif_ms') for row in rows]
        baseline, changed = statistics.mean(fixed), statistics.mean(adaptive)
        if baseline == 0:
            raise ValueError('Rata-rata pembanding tetap harus lebih besar dari nol')
        result.update(rata_rata_tetap_ms=baseline, rata_rata_adaptif_ms=changed,
                      penurunan_persen=100 * (baseline - changed) / baseline)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('klasifikasi', 'latensi', 'perbandingan'))
    parser.add_argument('csv', type=Path)
    parser.add_argument('--batas-ms', type=float)
    args = parser.parse_args()
    try:
        result = hitung(args.mode, args.csv, args.batas_ms)
    except (OSError, ValueError, csv.Error) as error:
        print(json.dumps(dict(status='ERROR',pesan=str(error)), ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

"""Compare the five reference nets in CSV, Wokwi, and the native Fritzing sketch."""
import argparse
import csv
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent

class Nets:
    def __init__(self): self.parent = {}
    def find(self, node):
        self.parent.setdefault(node, node)
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]
    def join(self, a, b): self.parent[self.find(a)] = self.find(b)
    def groups(self, labels=None):
        groups = {}
        for node in list(self.parent):
            if labels is None or node in labels:
                groups.setdefault(self.find(node), set()).add(labels[node] if labels else node)
        return {frozenset(g) for g in groups.values() if len(g) > 1}

def csv_nets(path):
    groups = {}
    seen = set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            pin = row["komponen"] + ":" + row["pin"]
            if pin in seen: raise ValueError("Pin ganda pada CSV: " + pin)
            seen.add(pin)
            groups.setdefault(row["net"],set()).add(pin)
    if len(groups) != 5: raise ValueError("Contoh memerlukan lima net; periksa label CSV.")
    return {frozenset(g) for g in groups.values()}

def wokwi_nets(path):
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    nets = Nets()
    for connection in document["connections"]:
        a,b = connection[:2]
        if a.startswith("$serialMonitor") or b.startswith("$serialMonitor"): continue
        nets.join(a,b)
    return nets.groups()

def fritzing_nets(path):
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read(next(n for n in archive.namelist() if n.endswith(".fz"))))
        parts = {}
        for name in archive.namelist():
            if name.endswith(".fzp"):
                p = ET.fromstring(archive.read(name))
                parts[p.attrib["moduleId"]] = {c.attrib["id"]:c.attrib["name"] for c in p.findall("connectors/connector")}
    nets = Nets(); labels = {}
    for instance in root.findall("instances/instance"):
        index = instance.attrib["modelIndex"]
        module = instance.attrib["moduleIdRef"]
        if module == "WireModuleID": nets.join((index,"connector0"),(index,"connector1"))
        else:
            name = module.removeprefix("mk38_p12_")
            for connector,pin in parts[module].items(): labels[(index,connector)] = name+":"+pin
        for c in instance.findall("views/schematicView/connectors/connector"):
            for other in c.findall("connects/connect"):
                nets.join((index,c.attrib["connectorId"]),(other.attrib["modelIndex"],other.attrib["connectorId"]))
    return nets.groups(labels)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pinmap",type=Path,default=HERE/"rangkaian/pinmap.csv")
    args = parser.parse_args()
    reference = csv_nets(args.pinmap)
    for name,actual in [("Wokwi",wokwi_nets(HERE/"rangkaian/diagram.json")),
                        ("Fritzing",fritzing_nets(HERE/"rangkaian/acuan_logika.fzz"))]:
        if actual != reference:
            missing = sorted(sorted(g) for g in reference-actual)
            extra = sorted(sorted(g) for g in actual-reference)
            raise ValueError(f"Net {name} berbeda. Belum cocok: {missing}; tambahan: {extra}")
    interface=json.loads((HERE/"desain/interface.json").read_text(encoding="utf-8-sig"))
    if interface["sensor"]["dht_gpio"] != 15 or interface["led"]["gpio"] != 23:
        raise ValueError("GPIO interface berbeda dari contoh yang diperiksa.")
    if interface["mqtt"]["command_retain"] is not False:
        raise ValueError("Perintah LED pada contoh harus tanpa retain.")
    print("PASS: pin map = Wokwi = Fritzing; 5 net, GPIO 15/23, command tanpa retain.")
    print("Batas: konektivitas logis; ukuran fisik, footprint PCB, dan perilaku firmware tidak diuji skrip ini.")

if __name__ == "__main__":
    try: main()
    except (ValueError,KeyError,OSError,ET.ParseError,zipfile.BadZipFile) as exc:
        print("GAGAL: " + str(exc),file=sys.stderr)
        raise SystemExit(1)

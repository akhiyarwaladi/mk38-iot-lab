"""Read-only view of the durable gateway queue."""
import argparse
import json
import sqlite3
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--db", type=Path, default=Path("runtime/gateway.sqlite"))
args = parser.parse_args()
try:
    with sqlite3.connect(args.db.resolve().as_uri() + "?mode=ro", uri=True) as db:
        counts = db.execute("SELECT COUNT(*),COALESCE(SUM(sent),0) FROM samples").fetchone()
        rows = db.execute("SELECT event_id,received_at,sent,payload FROM samples ORDER BY rowid DESC LIMIT 5").fetchall()
        print(json.dumps({"total": counts[0], "sent": counts[1], "pending": counts[0]-counts[1], "latest": rows}, indent=2))
except sqlite3.Error as error:
    raise SystemExit("Database belum siap: " + str(error))

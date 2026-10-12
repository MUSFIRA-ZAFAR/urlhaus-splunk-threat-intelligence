import json
from pathlib import Path
from storage import open_database
from delivery import deliver_pending

config = json.loads(Path("config/lab.json").read_text())
config["hec_token_file"] = "~/.config/ti-lab/synthetic-hec.token"
fixture = json.loads(Path("state/synthetic-events.json").read_text())

db = open_database("~/.local/state/ti-lab/synthetic.sqlite3")
db.execute("""
CREATE TABLE IF NOT EXISTS outbox (
    event_id TEXT PRIMARY KEY,
    ioc_id TEXT,
    target_index TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending','accepted')),
    attempts INTEGER NOT NULL DEFAULT 0,
    accepted_at REAL,
    last_error TEXT
)
""")

with db:
    for event in fixture["events"]:
        payload = {
            "time": event["observed_at"],
            "index": "ti_synthetic",
            "source": "ti_synthetic_generator",
            "sourcetype": "_json",
            "event": event,
        }
        db.execute("""
            INSERT OR IGNORE INTO outbox
            (event_id, target_index, payload_json, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            event["event_id"], "ti_synthetic",
            json.dumps(payload, allow_nan=False),
            fixture["generated_at"],
        ))

accepted = deliver_pending(db, config)
print("Accepted this run:", accepted)
print("Fixture run_id:", fixture["run_id"])
for row in db.execute("""
    SELECT status, COUNT(*) AS total FROM outbox GROUP BY status
"""):
    print(row["status"], row["total"])
db.close()

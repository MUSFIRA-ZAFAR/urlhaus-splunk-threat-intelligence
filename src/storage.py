import hashlib
import json
import os
import sqlite3
from pathlib import Path

def open_database(path):
    os.umask(0o077)
    db = sqlite3.connect(Path(path).expanduser(), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA synchronous=FULL")
    return db

def save_indicator(db, item, target_index):
    columns = tuple(item)
    with db:
        db.execute("BEGIN IMMEDIATE")
        old = db.execute(
            "SELECT * FROM indicators WHERE ioc_id=?", (item["ioc_id"],)
        ).fetchone()
        if old:
            if item["collected_at"] < old["collected_at"]:
                return "stale"
            unchanged = all(old[key] == item[key] for key in columns)
            if unchanged:
                return "duplicate"
        revision = old["revision"] + 1 if old else 1
        event_id = hashlib.sha256(
            f'{item["ioc_id"]}:{revision}'.encode()
        ).hexdigest()
        event = dict(item)
        event["metadata"] = json.loads(event.pop("metadata_json"))
        event.update(
            event_id=event_id, revision=revision,
            indicator_value=item["normalized_url"],
            expiry_policy="24h_from_collection" if
                item["expires_at"] - item["collected_at"] == 86400
                else "configured_ttl_from_collection",
            event_kind="indicator",
        )
        payload = {
            "time": item["collected_at"],
            "index": target_index,
            "sourcetype": "_json",
            "source": "urlhaus_collector",
            "event": event,
        }
        names = ",".join(columns)
        placeholders = ",".join("?" for _ in columns)
        updates = ",".join(
            f"{key}=excluded.{key}" for key in columns if key != "ioc_id"
        )
        db.execute(
            f"INSERT INTO indicators ({names},revision) "
            f"VALUES ({placeholders},?) "
            f"ON CONFLICT(ioc_id) DO UPDATE SET {updates},"
            "revision=excluded.revision",
            tuple(item[key] for key in columns) + (revision,),
        )
        db.execute(
            "INSERT INTO outbox "
            "(event_id,ioc_id,target_index,payload_json,created_at) "
            "VALUES (?,?,?,?,?)",
            (event_id, item["ioc_id"], target_index,
             json.dumps(payload, allow_nan=False), item["collected_at"]),
        )
    return "updated" if old else "inserted"

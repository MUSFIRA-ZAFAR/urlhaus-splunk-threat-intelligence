from app_logging import report
from health import queue_health
import json
import time
import uuid
from collections import Counter
from pathlib import Path

from feed import FeedError, FeedDeferred, fetch_with_cooldown
from records import prepare_record
from storage import open_database, save_indicator
from delivery import deliver_pending

def main():
    config = json.loads(Path("config/lab.json").read_text())
    db = open_database(config["database_file"])
    run_id = str(uuid.uuid4())
    started = time.time()
    counts = Counter()
    fetched = rejected = 0
    status = "success"
    error = None

    try:
        with db:
            db.execute(
                "INSERT INTO collection_runs (run_id,started_at,status) "
                "VALUES (?,?,?)", (run_id, started, "running")
            )
        try:
            records, collected_at = fetch_with_cooldown(db, config)
            fetched = len(records)
            for raw in records:
                try:
                    item = prepare_record(
                        raw, collected_at, config["ioc_ttl_hours"]
                    )
                except (ValueError, TypeError, OverflowError):
                    rejected += 1
                    continue
                result = save_indicator(db, item, config["ioc_index"])
                counts[result] += 1
            if rejected:
                status = "partial"
        except FeedDeferred as exc:
            status = "deferred"
            error = str(exc)
        except (FeedError, OSError) as exc:
            status = "failed"
            error = str(exc) if isinstance(exc, FeedError) else type(exc).__name__

        with db:
            db.execute(
                "UPDATE collection_runs SET finished_at=?,status=?,"
                "fetched=?,rejected=?,error=? WHERE run_id=?",
                (time.time(), status, fetched, rejected, error, run_id)
            )
        report("Collection:", status, "| fetched:", fetched,
              "| rejected:", rejected)
        report("Storage:", dict(counts))
        if error:
            report("Feed error:", error)
        queue_health(db, config, run_id)
        report("Accepted this run:", deliver_pending(db, config))
        report("Queue:", [
            tuple(row) for row in db.execute(
                "SELECT status,COUNT(*) FROM outbox GROUP BY status"
            )
        ])
    finally:
        db.close()

def run_locked():
    import fcntl
    import os

    os.umask(0o077)
    directory = Path.home() / ".local/state/ti-lab"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (directory / "collector.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            report("Run skipped: another collector holds the lock")
            return
        main()

if __name__ == "__main__":
    run_locked()

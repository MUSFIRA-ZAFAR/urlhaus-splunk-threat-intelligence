import json
import time

def queue_health(db, config, run_id):
    now = time.time()
    run = db.execute(
        "SELECT * FROM collection_runs WHERE run_id=?", (run_id,)
    ).fetchone()
    last_success = db.execute(
        "SELECT MAX(finished_at) FROM collection_runs "
        "WHERE status IN ('success','partial')"
    ).fetchone()[0]
    pending = db.execute(
        "SELECT COUNT(*),MIN(created_at),"
        "COALESCE(SUM(last_error IS NOT NULL),0) "
        "FROM outbox WHERE status='pending'"
    ).fetchone()
    event_id = f"health:{run_id}"
    event = {
        "event_id": event_id,
        "event_kind": "collector_health",
        "run_id": run_id,
        "collection_status": run["status"],
        "fetched": run["fetched"],
        "rejected": run["rejected"],
        "collection_error": run["error"],
        "last_successful_collection": last_success,
        "feed_age_seconds": now - last_success if last_success else None,
        "snapshot_phase": "before_delivery",
        "pending_before_delivery": pending[0],
        "failed_pending_before_delivery": pending[2],
        "oldest_pending_age_seconds":
            now - pending[1] if pending[1] is not None else 0,
    }
    payload = {
        "time": now,
        "index": config["health_index"],
        "sourcetype": "_json",
        "source": "urlhaus_collector",
        "event": event,
    }
    with db:
        db.execute(
            "INSERT OR IGNORE INTO outbox "
            "(event_id,target_index,payload_json,created_at) VALUES (?,?,?,?)",
            (event_id, config["health_index"],
             json.dumps(payload, allow_nan=False), now)
        )

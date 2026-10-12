import json
import time
from pathlib import Path
import requests
from cooldown import initialize, remaining, defer, retry_deadline

def deliver_pending(db, config):
    initialize(db)
    wait = remaining(db, "hec", time.time())
    if wait > 0:
        print(f"HEC delivery deferred: {wait:.0f}s remaining")
        return 0
    token = Path(config["hec_token_file"]).expanduser().read_text().strip()
    if not token:
        raise ValueError("HEC token file is empty")
    accepted = 0
    with requests.Session() as session:
        session.trust_env = False
        session.headers["Authorization"] = f"Splunk {token}"
        rows = db.execute(
            "SELECT * FROM outbox WHERE status='pending' "
            "ORDER BY created_at,event_id LIMIT 1000"
        ).fetchall()
        for row in rows:
            for attempt in range(config["max_delivery_attempts_per_run"]):
                with db:
                    db.execute(
                        "UPDATE outbox SET attempts=attempts+1 WHERE event_id=?",
                        (row["event_id"],),
                    )
                retry = True
                try:
                    with session.post(
                        config["hec_endpoint"],
                        json=json.loads(row["payload_json"]),
                        verify=str(Path(config["hec_ca_file"]).expanduser()),
                        timeout=(config["connect_timeout_seconds"],
                                 config["read_timeout_seconds"]),
                        allow_redirects=False,
                    ) as response:
                        if response.status_code == 200:
                            body = response.json()
                            if isinstance(body, dict) and body.get("code") == 0:
                                with db:
                                    db.execute(
                                        "UPDATE outbox SET status='accepted',"
                                        "accepted_at=?,last_error=NULL WHERE event_id=?",
                                        (time.time(), row["event_id"]),
                                    )
                                accepted += 1
                                break
                            error = "HEC response did not confirm acceptance"
                            retry = False
                        else:
                            error = f"HTTP {response.status_code}"
                            if response.status_code in (429, 503):
                                defer(db, "hec", retry_deadline(
                                    response.headers.get("Retry-After"), time.time()))
                                retry = False
                            else:
                                retry = response.status_code >= 500
                except (requests.RequestException, ValueError) as exc:
                    error = type(exc).__name__
                    retry = not isinstance(exc, requests.exceptions.SSLError)
                with db:
                    db.execute(
                        "UPDATE outbox SET last_error=? WHERE event_id=?",
                        (error, row["event_id"]),
                    )
                if not retry or attempt + 1 == config["max_delivery_attempts_per_run"]:
                    print("Delivery paused:", error, "| records remain pending")
                    return accepted
                time.sleep(2 ** (attempt + 1))
    return accepted

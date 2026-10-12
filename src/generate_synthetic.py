import csv
import ipaddress
import json
import time
import uuid
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from normalize import normalize_url

output = Path("state/synthetic-events.json")
if output.exists():
    raise SystemExit("Fixture already exists; keep it for reproducible retries.")

with Path("state/ti-active-snapshot.csv").open(newline="") as file:
    rows = list(csv.DictReader(file))

now = time.time()
domains = []
for row in rows:
    if float(row["expires_at"]) <= now:
        continue
    try:
        ipaddress.ip_address(row["hostname"])
    except ValueError:
        domains.append(row)

seed = sorted(domains, key=lambda r: int(r["source_record_id"]))[0]
url = seed["normalized_url"]
parts = urlsplit(url)
changed = urlunsplit(parts._replace(path=parts.path.swapcase()))
different = urlunsplit(parts._replace(path="/ti-lab-synthetic-only", query="", fragment=""))
known = {row["normalized_url"] for row in rows}
assert changed != url and changed not in known
assert different not in known

cases = [
    ("proxy_exact", "proxy", url, "exact_url"),
    ("proxy_path_case", "proxy", changed, "hostname_only"),
    ("proxy_other_path", "proxy", different, "hostname_only"),
    ("proxy_nonmatch", "proxy", "https://example.invalid/safe", "no_match"),
    ("dns_hostname", "dns", seed["hostname"], "hostname_only"),
    ("dns_nonmatch", "dns", "example.invalid", "no_match"),
]
run_id = str(uuid.uuid4())
events = []
for name, kind, destination, expected in cases:
    event = dict(
        event_id=str(uuid.uuid5(uuid.UUID(run_id), name)),
        run_id=run_id, test_case=name, event_kind="activity",
        synthetic=True, activity_type=kind, device="synthetic-device-01",
        observed_at=now, expected_match=expected,
    )
    if kind == "proxy":
        normalized = normalize_url(destination)
        event.update(observed_url=destination,
                     normalized_url=normalized["normalized_url"],
                     hostname=normalized["hostname"])
    else:
        event["hostname"] = destination
    events.append(event)

output.write_text(json.dumps(
    {"run_id": run_id, "generated_at": now, "events": events},
    indent=2, allow_nan=False
) + "\n")
print("Saved:", output)
for event in events:
    print(event["test_case"], "=>", event["expected_match"])
print("Events:", len(events))

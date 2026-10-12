import hashlib
import json
import math
from datetime import datetime, timezone
from normalize import normalize_url

def prepare_record(record, collected_at, ttl_hours):
    if not isinstance(record, dict):
        raise ValueError("Record must be an object")
    source_id = record.get("id")
    if isinstance(source_id, bool) or not isinstance(source_id, (str, int)):
        raise ValueError("Invalid source record ID")
    source_id = str(source_id)
    if not source_id.isascii() or not source_id.isdigit():
        raise ValueError("Source record ID must contain digits")
    status = record.get("url_status")
    if status not in ("online", "offline", "unknown"):
        raise ValueError("Invalid provider status")
    if record.get("threat") != "malware_download":
        raise ValueError("Unsupported threat type")
    added = record.get("date_added")
    if not isinstance(added, str):
        raise ValueError("Missing provider timestamp")
    provider_time = datetime.strptime(added, "%Y-%m-%d %H:%M:%S UTC")
    provider_time = provider_time.replace(tzinfo=timezone.utc)
    if not math.isfinite(collected_at) or collected_at <= 0:
        raise ValueError("Invalid collection time")
    if not math.isfinite(ttl_hours) or ttl_hours <= 0:
        raise ValueError("Invalid expiry policy")
    url = normalize_url(record.get("url"))
    return {
        "ioc_id": hashlib.sha256(f"URLhaus:{source_id}".encode()).hexdigest(),
        "source": "URLhaus",
        "source_record_id": source_id,
        "indicator_type": "url",
        **url,
        "provider_date_added": provider_time.isoformat(),
        "provider_status": status,
        "metadata_json": json.dumps(record, sort_keys=True, allow_nan=False),
        "collected_at": collected_at,
        "expires_at": collected_at + ttl_hours * 3600,
    }

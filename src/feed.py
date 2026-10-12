import time
from pathlib import Path
import requests

class FeedError(RuntimeError):
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after

def fetch_recent(config):
    endpoint = "https://urlhaus-api.abuse.ch/v1/urls/recent/limit/3/"
    if config["urlhaus_endpoint"] != endpoint:
        raise FeedError("Unsupported API endpoint")
    key = Path(config["urlhaus_key_file"]).expanduser().read_text().strip()
    if not key:
        raise FeedError("API key file is empty")

    try:
        with requests.Session() as session:
            session.trust_env = False
            with session.get(
                endpoint,
                headers={"Auth-Key": key},
                timeout=(config["connect_timeout_seconds"],
                         config["read_timeout_seconds"]),
                allow_redirects=False,
            ) as response:
                if response.status_code == 429:
                    raise FeedError(
                        "HTTP 429: stop collection; rate limited",
                        retry_after=response.headers.get("Retry-After"),
                    )
                if response.status_code != 200:
                    raise FeedError(f"API HTTP {response.status_code}")
                try:
                    body = response.json()
                except ValueError:
                    raise FeedError("API returned invalid JSON") from None
    except requests.RequestException as exc:
        raise FeedError(type(exc).__name__) from None

    if not isinstance(body, dict):
        raise FeedError("API response must be an object")
    if body.get("query_status") == "no_results":
        return [], time.time()
    if body.get("query_status") != "ok":
        raise FeedError("API query_status is not ok")
    records = body.get("urls")
    if not isinstance(records, list) or len(records) > 3:
        raise FeedError("Invalid API record list")
    return records, time.time()

class FeedDeferred(FeedError):
    pass

def fetch_with_cooldown(db, config):
    from cooldown import initialize, remaining, defer, retry_deadline

    initialize(db)
    wait = remaining(db, "urlhaus", time.time())
    if wait > 0:
        raise FeedDeferred(f"Collection deferred: {wait:.0f}s remaining")
    try:
        return fetch_recent(config)
    except FeedError as exc:
        now = time.time()
        defer(db, "urlhaus", retry_deadline(exc.retry_after, now))
        raise

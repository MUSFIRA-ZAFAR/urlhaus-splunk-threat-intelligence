import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from delivery import deliver_pending
from storage import open_database

class DeliveryCooldownTests(unittest.TestCase):
    def test_cooldown_and_recovery(self):
        for http in (429, 503):
            with self.subTest(http=http), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                token = root / "dummy.token"
                token.write_text("synthetic-test-token")
                config = {
                    "hec_token_file": str(token),
                    "hec_ca_file": str(root / "unused.crt"),
                    "hec_endpoint": "https://127.0.0.1:8088/services/collector/event",
                    "connect_timeout_seconds": 5,
                    "read_timeout_seconds": 20,
                    "max_delivery_attempts_per_run": 3,
                }
                path = root / "test.sqlite3"
                db = open_database(path)
                db.executescript(Path("config/schema.sql").read_text())
                with db:
                    db.execute(
                        "INSERT INTO outbox "
                        "(event_id,target_index,payload_json,created_at) "
                        "VALUES (?,?,?,?)",
                        ("test-event", "ti_health",
                         json.dumps({"event": {"synthetic": True}}), 1000)
                    )

                with patch("delivery.time.time", return_value=1000):
                    with patch("delivery.requests.Session") as factory:
                        session = factory.return_value.__enter__.return_value
                        response = session.post.return_value.__enter__.return_value
                        response.status_code = http
                        response.headers = {"Retry-After": "120"}
                        self.assertEqual(deliver_pending(db, config), 0)
                        session.post.assert_called_once()
                row = db.execute("SELECT status,attempts FROM outbox").fetchone()
                self.assertEqual(tuple(row), ("pending", 1))
                db.close()

                db = open_database(path)
                with patch("delivery.time.time", return_value=1010):
                    with patch("delivery.requests.Session") as factory:
                        self.assertEqual(deliver_pending(db, config), 0)
                        factory.assert_not_called()

                with patch("delivery.time.time", return_value=1121):
                    with patch("delivery.requests.Session") as factory:
                        session = factory.return_value.__enter__.return_value
                        response = session.post.return_value.__enter__.return_value
                        response.status_code = 200
                        response.json.return_value = {"code": 0}
                        self.assertEqual(deliver_pending(db, config), 1)
                        session.post.assert_called_once()
                row = db.execute(
                    "SELECT status,attempts,last_error FROM outbox"
                ).fetchone()
                self.assertEqual(tuple(row), ("accepted", 2, None))
                db.close()

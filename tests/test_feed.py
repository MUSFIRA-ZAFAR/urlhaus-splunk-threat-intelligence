import unittest
from unittest.mock import patch
import requests
from feed import FeedError, fetch_recent

CONFIG = {
    "urlhaus_endpoint":
        "https://urlhaus-api.abuse.ch/v1/urls/recent/limit/3/",
    "urlhaus_key_file": "/unused/dummy.key",
    "connect_timeout_seconds": 5,
    "read_timeout_seconds": 20,
}

class FeedFailureTests(unittest.TestCase):
    def simulate(self, http=200, bad_json=False, timeout=False):
        with patch("feed.Path.read_text", return_value="dummy-test-key"):
            with patch("feed.requests.Session") as factory:
                session = factory.return_value.__enter__.return_value
                response = session.get.return_value.__enter__.return_value
                response.status_code = http
                response.headers = {"Retry-After": "120"}
                if bad_json:
                    response.json.side_effect = ValueError("simulated")
                if timeout:
                    session.get.side_effect = requests.Timeout()
                return fetch_recent(CONFIG)

    def test_authentication_failure(self):
        with self.assertRaisesRegex(FeedError, "HTTP 401"):
            self.simulate(http=401)

    def test_rate_limit(self):
        with self.assertRaises(FeedError) as caught:
            self.simulate(http=429)
        self.assertEqual(caught.exception.retry_after, "120")

    def test_malformed_json(self):
        with self.assertRaisesRegex(FeedError, "invalid JSON"):
            self.simulate(bad_json=True)

    def test_timeout(self):
        with self.assertRaisesRegex(FeedError, "Timeout"):
            self.simulate(timeout=True)

if __name__ == "__main__":
    unittest.main()

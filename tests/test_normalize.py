import unittest
from normalize import normalize_url

class NormalizationTests(unittest.TestCase):
    def test_preserve_original_and_suffix(self):
        original = "HTTP://EXAMPLE.com:8080/Download?ID=AbC&x=%2F"
        result = normalize_url(original)
        self.assertEqual(result["original_url"], original)
        self.assertEqual(
            result["normalized_url"],
            "http://example.com:8080/Download?ID=AbC&x=%2F",
        )

    def test_case_sensitive_path_and_query(self):
        for first, second in [
            ("https://example.com/A", "https://example.com/a"),
            ("https://example.com/?ID=AbC", "https://example.com/?ID=abc"),
        ]:
            self.assertNotEqual(
                normalize_url(first)["normalized_url"],
                normalize_url(second)["normalized_url"],
            )

    def test_fragment_policy(self):
        result = normalize_url("https://EXAMPLE.com/A?#section")
        self.assertEqual(result["normalized_url"], "https://example.com/A?")
        self.assertTrue(result["original_url"].endswith("#section"))

    def test_ip_hosts(self):
        for host in ["192.0.2.10", "[2001:db8::1]"]:
            url = f"https://{host}/A"
            self.assertEqual(normalize_url(url)["normalized_url"], url)

    def test_reject_invalid_or_unsupported(self):
        for url in [
            "", None, "ftp://example.com/a", "http:///a",
            "http://example.com:99999/a", "http://example.com:/a",
            "http://user:pass@example.com/a", "http://example.com/a\n",
            "http://example.com\\a", "http://-invalid.example/a",
        ]:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    normalize_url(url)

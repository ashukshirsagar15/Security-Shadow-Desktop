import unittest

from local_config import resolve_local_backend_url


class LocalBackendURLTests(unittest.TestCase):
    def test_default_loopback_url_is_allowed(self):
        self.assertEqual(
            resolve_local_backend_url(
                "SECURITY_SHADOW_BACKEND_URL", "http://127.0.0.1:5001", {}
            ),
            "http://127.0.0.1:5001",
        )

    def test_localhost_url_is_allowed_and_trailing_slash_removed(self):
        self.assertEqual(
            resolve_local_backend_url(
                "SECURITY_SHADOW_BACKEND_URL", "http://127.0.0.1:5001",
                {"SECURITY_SHADOW_BACKEND_URL": "http://localhost:5011/"},
            ),
            "http://localhost:5011",
        )

    def test_remote_backend_unsafe_schemes_and_invalid_ports_are_rejected(self):
        unsafe_urls = (
            "http://example.com:5001",
            "https://127.0.0.1:5001",
            "ftp://127.0.0.1:5001",
            "http://127.0.0.1:99999",
        )
        for url in unsafe_urls:
            with self.subTest(url=url):
                with self.assertRaises(RuntimeError):
                    resolve_local_backend_url(
                        "SECURITY_SHADOW_BACKEND_URL",
                        "http://127.0.0.1:5001",
                        {"SECURITY_SHADOW_BACKEND_URL": url},
                    )

    def test_url_with_embedded_credentials_is_rejected(self):
        with self.assertRaises(RuntimeError):
            resolve_local_backend_url(
                "SECURITY_SHADOW_BACKEND_URL", "http://127.0.0.1:5001",
                {"SECURITY_SHADOW_BACKEND_URL": "http://user:secret@127.0.0.1:5001"},
            )


if __name__ == "__main__":
    unittest.main()

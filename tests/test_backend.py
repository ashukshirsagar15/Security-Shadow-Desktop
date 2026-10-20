import unittest
from unittest.mock import patch

from private_backend import app as backend


UPLOAD_TOKEN = "U" * 48
READ_TOKEN = "R" * 48


class BackendTests(unittest.TestCase):
    def setUp(self):
        backend.app.config.update(TESTING=True)
        with backend.snapshot_lock:
            backend.latest_snapshot = None
        self.client = backend.app.test_client()
        self.secret_patch = patch.object(
            backend, "read_secret",
            side_effect=lambda filename: {
                ".upload_token": UPLOAD_TOKEN,
                ".read_token": READ_TOKEN,
            }.get(filename, ""),
        )
        self.secret_patch.start()
        self.addCleanup(self.secret_patch.stop)

    def test_upload_without_token_is_rejected(self):
        response = self.client.post("/api/agent/snapshot", json={})
        self.assertEqual(response.status_code, 401)

    def test_valid_snapshot_upload_and_private_read(self):
        payload = {
            "timestamp": "2026-01-01T00:00:00+00:00",
            "computer_data": {
                "processes": [{"pid": 99, "name": "chrome.exe"}],
                "connections": [{
                    "pid": 99,
                    "process_name": "chrome.exe",
                    "remote_ip": "192.0.2.10",
                    "remote_port": 443,
                    "status": "ESTABLISHED",
                }],
                "network_note": None,
            },
        }
        headers = {"Authorization": f"Bearer {UPLOAD_TOKEN}"}
        upload = self.client.post("/api/agent/snapshot", json=payload, headers=headers)
        self.assertEqual(upload.status_code, 202)
        self.assertTrue(upload.json["accepted"])

        read = self.client.get("/api/private/snapshot", headers={"Authorization": f"Bearer {READ_TOKEN}"})
        self.assertEqual(read.status_code, 200)
        self.assertTrue(read.json["available"])
        connection = read.json["snapshot"]["computer_data"]["connections"][0]
        self.assertEqual(connection["risk_level"], "LOW")
        self.assertIn("risk_reasons", connection)

    def test_malformed_snapshot_is_rejected(self):
        headers = {"Authorization": f"Bearer {UPLOAD_TOKEN}"}
        response = self.client.post(
            "/api/agent/snapshot",
            json={"timestamp": "now", "computer_data": {"processes": [], "connections": "not a list"}},
            headers=headers,
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()

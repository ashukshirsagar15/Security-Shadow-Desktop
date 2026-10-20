import unittest
from unittest.mock import Mock, patch

import app as dashboard


class DashboardTests(unittest.TestCase):
    def setUp(self):
        dashboard.app.config.update(TESTING=True)
        self.client = dashboard.app.test_client()
        self.token_patch = patch.object(
            dashboard, "read_read_token", return_value="R" * 48
        )
        self.token_patch.start()
        self.addCleanup(self.token_patch.stop)

    def test_snapshot_fields_are_mapped_for_dashboard(self):
        response_stub = Mock()
        response_stub.status_code = 200
        response_stub.ok = True
        response_stub.json.return_value = {
            "available": True,
            "snapshot": {
                "timestamp": "2026-01-01T00:00:00+00:00",
                "computer_data": {
                    "network_note": None,
                    "connections": [{
                        "process_name": "chrome.exe",
                        "pid": 41,
                        "remote_ip": "192.0.2.4",
                        "remote_port": 443,
                        "risk_score": 0,
                        "risk_level": "LOW",
                        "risk_reasons": [
                            "No configured heuristic was triggered"
                        ],
                    }],
                },
            },
        }

        with patch.object(
            dashboard.requests, "get", return_value=response_stub
        ) as mock_get:
            response = self.client.get("/api/connections")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["connected"])
        self.assertEqual(
            response.json["connections"][0]["process"], "chrome.exe"
        )
        self.assertEqual(
            response.json["connections"][0]["reasons"],
            ["No configured heuristic was triggered"],
        )
        self.assertTrue(
            mock_get.call_args.kwargs["headers"]["Authorization"].startswith(
                "Bearer "
            )
        )

    def test_dashboard_page_serves_html(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"LOCAL SECURITY MONITOR", response.data)
        self.assertIn(b"WHY FLAGGED", response.data)
        self.assertIn(
            b"No configured heuristic was triggered", response.data
        )


if __name__ == "__main__":
    unittest.main()

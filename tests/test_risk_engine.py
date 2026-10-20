import unittest
from unittest.mock import patch

from risk_engine import score_connection, score_snapshot


class RiskEngineTests(unittest.TestCase):
    def test_common_browser_connection_is_low(self):
        result = score_connection({
            "process_name": "chrome.exe",
            "remote_ip": "192.0.2.10",
            "remote_port": 443,
        })

        self.assertEqual(result["risk_level"], "LOW")
        self.assertEqual(result["risk_score"], 0)
        self.assertEqual(
            result["risk_reasons"],
            ["No configured heuristic was triggered"],
        )

    def test_unknown_process_on_common_port_gets_small_score(self):
        result = score_connection({
            "process_name": "custom_app.exe",
            "remote_ip": "192.0.2.20",
            "remote_port": 443,
        })

        self.assertEqual(result["risk_score"], 5)
        self.assertEqual(result["risk_level"], "LOW")
        self.assertIn(
            "Process is not in the initial known-process list",
            result["risk_reasons"],
        )

    def test_suspicious_name_and_unusual_port_are_explained(self):
        result = score_connection({
            "process_name": "keylogger_demo.exe",
            "remote_ip": "192.0.2.30",
            "remote_port": 4444,
        })

        self.assertEqual(result["risk_score"], 40)
        self.assertEqual(result["risk_level"], "MEDIUM")
        self.assertIn(
            "Process is not in the initial known-process list",
            result["risk_reasons"],
        )
        self.assertIn(
            "Process name matches a suspicious-name heuristic",
            result["risk_reasons"],
        )
        self.assertIn(
            "Remote port is not in the common-port list",
            result["risk_reasons"],
        )

    def test_configured_review_ip_is_explained(self):
        with patch("risk_engine.SUSPICIOUS_IPS", {"192.0.2.40"}):
            result = score_connection({
                "process_name": "chrome.exe",
                "remote_ip": "192.0.2.40",
                "remote_port": 443,
            })

        self.assertEqual(result["risk_score"], 40)
        self.assertEqual(result["risk_level"], "MEDIUM")
        self.assertIn(
            "Remote IP matches the configured review list",
            result["risk_reasons"],
        )

    def test_invalid_remote_port_type_is_explained(self):
        result = score_connection({
            "process_name": "chrome.exe",
            "remote_ip": "192.0.2.10",
            "remote_port": "443",
        })

        self.assertEqual(result["risk_score"], 10)
        self.assertIn(
            "Remote port has an invalid data type",
            result["risk_reasons"],
        )

    def test_snapshot_gets_summary_and_does_not_mutate_input(self):
        snapshot = {
            "timestamp": "2026-01-01T00:00:00+00:00",
            "computer_data": {
                "processes": [],
                "connections": [{
                    "process_name": "chrome.exe",
                    "pid": 100,
                    "remote_ip": "192.0.2.5",
                    "remote_port": 443,
                }],
            },
        }

        assessed = score_snapshot(snapshot)

        self.assertEqual(
            len(assessed["computer_data"]["connections"]), 1
        )
        self.assertEqual(
            assessed["computer_data"]["risk_summary"]["assessed_connections"],
            1,
        )
        self.assertEqual(
            assessed["computer_data"]["risk_summary"]["low_risk"], 1
        )
        self.assertNotIn(
            "risk_score", snapshot["computer_data"]["connections"][0]
        )
        self.assertIn(
            "risk_score", assessed["computer_data"]["connections"][0]
        )


if __name__ == "__main__":
    unittest.main()

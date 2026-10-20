
"""Explainable heuristic risk scoring for Security Shadow."""

import ipaddress
import os
import re


# These are investigation signals, not proof of malicious activity.
KNOWN_PROCESSES = {
    "chrome.exe",
    "msedge.exe",
    "msedgewebview2.exe",
    "firefox.exe",
    "spotify.exe",
    "onedrive.exe",
    "code.exe",
    "svchost.exe",
    "explorer.exe",
    "officeclicktorun.exe",
    "filecoauth.exe",
    "taskhostw.exe",
}

COMMON_REMOTE_PORTS = {
    53, 80, 123, 443, 465, 587, 853, 993, 995, 5222, 5228,
}

SUSPICIOUS_NAME_PATTERNS = (
    "keylog",
    "stealer",
    "cryptominer",
    "backdoor",
    "injector",
)

# A configurable threshold: use only if the environment has a
# justified, reviewed list of endpoints to investigate.
SUSPICIOUS_IPS = {
    item.strip()
    for item in os.getenv("SECURITY_SHADOW_SUSPICIOUS_IPS", "").split(",")
    if item.strip()
}


def score_connection(connection):
    """Return a score, level, and explainable reasons for a connection."""
    score = 0
    reasons = []

    process_name = str(connection.get("process_name") or "Unknown")
    normalized_name = os.path.basename(process_name).lower()
    remote_ip = connection.get("remote_ip")
    remote_port = connection.get("remote_port")

    # A process name is context, not a reliable identity on its own.
    if normalized_name == "unknown":
        score += 10
        reasons.append("Process name unavailable")
    elif normalized_name not in KNOWN_PROCESSES:
        score += 5
        reasons.append("Process is not in the initial known-process list")

    if any(pattern in normalized_name for pattern in SUSPICIOUS_NAME_PATTERNS):
        score += 25
        reasons.append("Process name matches a suspicious-name heuristic")

    if isinstance(remote_port, int) and not isinstance(remote_port, bool):
        if not 1 <= remote_port <= 65535:
            score += 15
            reasons.append("Remote port is outside the valid range")
        elif remote_port not in COMMON_REMOTE_PORTS:
            score += 10
            reasons.append("Remote port is not in the common-port list")
    elif remote_port is not None:
        score += 10
        reasons.append("Remote port has an invalid data type")

    if isinstance(remote_ip, str) and remote_ip:
        try:
            address = ipaddress.ip_address(remote_ip)
            if str(address) in SUSPICIOUS_IPS:
                score += 40
                reasons.append("Remote IP matches the configured review list")
        except ValueError:
            score += 15
            reasons.append("Remote IP address is malformed")
    elif remote_ip is not None:
        score += 10
        reasons.append("Remote IP has an invalid data type")

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": score,
        "risk_level": level,
        "risk_reasons": reasons or ["No configured heuristic was triggered"],
    }


def score_snapshot(snapshot):
    """Add risk assessments to connection records in a snapshot copy."""
    result = dict(snapshot)
    computer_data = dict(snapshot.get("computer_data", {}))
    connections = computer_data.get("connections", [])

    assessed_connections = []

    for connection in connections:
        assessed = dict(connection)
        assessed.update(score_connection(connection))
        assessed_connections.append(assessed)

    computer_data["connections"] = assessed_connections
    computer_data["risk_summary"] = {
        "assessed_connections": len(assessed_connections),
        "high_risk": sum(
            item["risk_level"] == "HIGH"
            for item in assessed_connections
        ),
        "medium_risk": sum(
            item["risk_level"] == "MEDIUM"
            for item in assessed_connections
        ),
        "low_risk": sum(
            item["risk_level"] == "LOW"
            for item in assessed_connections
        ),
        "method": "heuristic",
    }

    result["computer_data"] = computer_data
    return result

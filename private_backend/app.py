
import hmac
import os
from threading import Lock

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flask import Flask, jsonify, request
from risk_engine import score_snapshot

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

latest_snapshot = None
snapshot_lock = Lock()

DATA_DIR = os.environ.get("SECURITY_SHADOW_DATA_DIR")
BASE_DIR = (os.path.join(DATA_DIR, "private_backend") if DATA_DIR else os.path.dirname(os.path.abspath(__file__)))


def read_secret(filename):
    """Read a secret from its private local file."""
    try:
        with open(
            os.path.join(BASE_DIR, filename),
            "r",
            encoding="utf-8",
        ) as file:
            return file.read().strip()
    except OSError:
        return ""


def authorized(filename):
    """Check the bearer token for one specific permission."""
    expected = read_secret(filename)
    header = request.headers.get("Authorization", "")
    prefix = "Bearer "

    if len(expected) < 32 or not header.startswith(prefix):
        return False

    supplied = header[len(prefix):]
    return hmac.compare_digest(supplied, expected)


def error_response(message, status):
    return jsonify({"error": message}), status


@app.errorhandler(413)
def request_too_large(_error):
    return error_response("Request body too large", 413)


@app.get("/health")
def health():
    return jsonify({
        "service": "Security Shadow Private Backend",
        "status": "running",
    })


@app.post("/api/agent/snapshot")
def receive_snapshot():
    global latest_snapshot

    if not authorized(".upload_token"):
        return error_response("Unauthorized", 401)

    if not request.is_json:
        return error_response(
            "Content-Type must be application/json", 415
        )

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return error_response("Invalid JSON object", 400)

    if not isinstance(payload.get("timestamp"), str):
        return error_response("Missing or invalid timestamp", 400)

    computer_data = payload.get("computer_data")
    if not isinstance(computer_data, dict):
        return error_response(
            "Missing computer_data object", 400
        )

    processes = computer_data.get("processes")
    connections = computer_data.get("connections")

    if not isinstance(processes, list) or not isinstance(connections, list):
        return error_response(
            "Processes and connections must be lists", 400
        )

    if len(processes) > 2000 or len(connections) > 2000:
        return error_response(
            "Snapshot contains too many records", 400
        )

    if not all(isinstance(item, dict) for item in processes):
        return error_response("Invalid process record", 400)

    if not all(isinstance(item, dict) for item in connections):
        return error_response("Invalid connection record", 400)

    # Store only after the basic checks pass.
    # Assess connections only after authentication and validation pass.
    assessed_snapshot = score_snapshot(payload)

    # Store the assessed snapshot.
    with snapshot_lock:
        latest_snapshot = assessed_snapshot

    return jsonify({
        "accepted": True,
        "process_count": len(processes),
        "connection_count": len(connections),
    }), 202



@app.get("/api/private/snapshot")
def read_private_snapshot():
    if not authorized(".read_token"):
        return error_response("Unauthorized", 401)

    # Safely retrieve the latest assessed snapshot.
    with snapshot_lock:
        snapshot = latest_snapshot

    if snapshot is None:
        return jsonify({
            "available": False,
            "message": "No snapshot received yet",
        })

    return jsonify({
        "available": True,
        "snapshot": snapshot,
    })


if __name__ == "__main__":
    if len(read_secret(".upload_token")) < 32:
        raise RuntimeError("Upload credential is missing or invalid. Run setup_local.py first.")

    if len(read_secret(".read_token")) < 32:
        raise RuntimeError("Read credential is missing or invalid. Run setup_local.py first.")

    # Local personal monitoring only. Do not expose this server publicly.
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("SECURITY_SHADOW_BACKEND_PORT", "5001")),
        debug=False,
        use_reloader=False,
    )
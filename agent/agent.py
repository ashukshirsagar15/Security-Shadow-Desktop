import os
import sys
import requests
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from local_config import resolve_local_backend_url

REFRESH_SECONDS = 5
# Uploading stays disabled unless explicitly enabled.
UPLOAD_ENABLED = os.getenv("SECURITY_SHADOW_UPLOAD", "false").lower() == "true"

BACKEND_URL = resolve_local_backend_url(
    "SECURITY_SHADOW_BACKEND_URL", "http://127.0.0.1:5001"
)

DATA_DIR = Path(os.environ.get("SECURITY_SHADOW_DATA_DIR", ROOT_DIR))
TOKEN_FILE = DATA_DIR / "private_backend" / ".upload_token"

def collect_processes():
    """Collect a snapshot of running process names and basic metadata."""
    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "status"]
    ):
        try:
            info = process.info

            processes.append({
                "pid": info.get("pid"),
                "name": info.get("name") or "Unknown",
                "status": info.get("status") or "Unknown",
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied,
                psutil.ZombieProcess):
            continue

    return processes



def collect_network_connections():
    """Collect established internet connections and their endpoints."""
    connections = []

    try:
        active_connections = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, OSError) as error:
        return [], f"Network collection unavailable: {type(error).__name__}"

    for connection in active_connections:
        if connection.status != "ESTABLISHED":
            continue

        if connection.pid is None:
            continue

        try:
            process_name = psutil.Process(connection.pid).name()
        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            process_name = "Unknown"

        local = connection.laddr
        remote = connection.raddr

        connections.append({
            "pid": connection.pid,
            "process_name": process_name,
            "local_ip": local.ip if local else None,
            "local_port": local.port if local else None,
            "remote_ip": remote.ip if remote else None,
            "remote_port": remote.port if remote else None,
            "status": connection.status,
        })

    return connections, None



def collect_snapshot():
    """Build one timestamped snapshot from this computer."""
    processes = collect_processes()
    connections, network_note = collect_network_connections()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "computer_data": {
            "process_count": len(processes),
            "connection_count": len(connections),
            "processes": processes,
            "connections": connections,
            "network_note": network_note,
        },
    }


def upload_snapshot(snapshot, log_callback=print):
    """Send one snapshot to the configured local backend when enabled."""
    if not UPLOAD_ENABLED:
        return

    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as file:
            token = file.read().strip()

        if len(token) < 32:
            log_callback("Upload skipped: backend token is missing or invalid.")
            return

        response = requests.post(
            f"{BACKEND_URL}/api/agent/snapshot",
            json=snapshot,
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )

        if response.status_code == 202:
            log_callback("Snapshot uploaded successfully.")
        else:
            log_callback(f"Upload failed: HTTP {response.status_code}.")

    except (OSError, requests.RequestException) as error:
        log_callback(f"Upload unavailable: {type(error).__name__}.")
def run_agent_loop(stop_event=None, log_callback=print):
    """Collect and upload snapshots until stopped; a stop event enables clean desktop shutdown."""
    while stop_event is None or not stop_event.is_set():
        snapshot = collect_snapshot()
        upload_snapshot(snapshot, log_callback=log_callback)
        data = snapshot["computer_data"]

        log_callback(f"Snapshot: {snapshot['timestamp']}")
        log_callback(f"Running processes collected: {data['process_count']}")
        log_callback(f"Established connections collected: {data['connection_count']}")

        if data["network_note"]:
            log_callback(data["network_note"])

        if stop_event is None:
            time.sleep(REFRESH_SECONDS)
        elif stop_event.wait(REFRESH_SECONDS):
            break


def main():
    print("=" * 55)
    print("SECURITY SHADOW - LOCAL AGENT")
    print(
        "Snapshot upload: "
        + ("ENABLED" if UPLOAD_ENABLED else "DISABLED (set SECURITY_SHADOW_UPLOAD=true to enable)")
    )
    print("Press Ctrl+C to stop.")
    print("=" * 55)

    try:
        run_agent_loop()
    except KeyboardInterrupt:
        print("\nAgent stopped safely.")


if __name__ == "__main__":
    main()
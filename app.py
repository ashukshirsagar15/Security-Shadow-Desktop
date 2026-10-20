"""Security Shadow local dashboard.

This dashboard proxies the private backend from the server side so the read
credential never reaches browser JavaScript. It is deliberately bound to
127.0.0.1 when run directly.
"""

import os
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template_string

from local_config import resolve_local_backend_url

BASE_DIR = Path(__file__).resolve().parent
BACKEND_URL = resolve_local_backend_url(
    "SECURITY_SHADOW_BACKEND_URL", "http://127.0.0.1:5001"
)
READ_TOKEN_FILE = BASE_DIR / "private_backend" / ".read_token"

app = Flask(__name__)

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Security Shadow | Local Monitor</title>
<style>
:root{--bg:#0b1120;--panel:#111b2e;--border:#24334a;--text:#e5edf8;--muted:#8da2bd;--green:#4ade80;--yellow:#facc15;--red:#f87171;--blue:#60a5fa}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Arial,sans-serif}header{padding:24px 5%;display:flex;justify-content:space-between;align-items:center;gap:16px;border-bottom:1px solid var(--border)}h1{margin:0;font-size:24px;letter-spacing:1px}h1 span{color:var(--green)}.subtitle{color:var(--muted);margin-top:8px;font-size:13px}.status{color:var(--yellow);font-size:13px;white-space:nowrap}main{padding:28px 5%}.section-title{font-size:17px;margin:0 0 18px}.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-bottom:30px}.card,.panel{background:var(--panel);border:1px solid var(--border);border-radius:12px}.card{padding:20px}.card-label{color:var(--muted);font-size:13px}.card-value{font-size:30px;font-weight:bold;margin-top:12px}.card-note{color:var(--muted);font-size:12px;margin-top:8px}.panel{overflow:hidden;margin-bottom:24px}.panel-header{padding:20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}.panel-header h2{margin:0;font-size:16px}.panel-header p{color:var(--muted);font-size:12px;margin:6px 0 0}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;text-align:left}th,td{padding:15px 20px;border-bottom:1px solid var(--border);font-size:13px;white-space:nowrap}th{color:var(--muted);font-weight:normal}.reason-cell{white-space:normal;min-width:260px;max-width:420px;line-height:1.5;overflow-wrap:anywhere}tbody tr:last-child td{border-bottom:none}.empty{text-align:center;color:var(--muted);padding:36px 20px}.badge{display:inline-block;padding:5px 9px;border-radius:20px;font-size:11px;font-weight:bold}.low{color:var(--green);background:#123526}.medium{color:var(--yellow);background:#3b3212}.high,.critical{color:var(--red);background:#401d27}.footer{padding:10px 5% 28px;color:var(--muted);font-size:12px}.notice{padding:16px 20px;color:var(--muted);font-size:13px;line-height:1.5}@media(max-width:900px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:520px){header{align-items:flex-start;flex-direction:column}.cards{grid-template-columns:1fr 1fr;gap:10px}.card{padding:14px}.card-value{font-size:24px}main{padding-top:20px}}
</style>
</head>
<body>
<header><div><h1>SECURITY <span>SHADOW</span></h1><div class="subtitle">LOCAL SECURITY MONITOR · LIVE AGENT DATA</div></div><div id="connection-status" class="status">● CHECKING BACKEND</div></header>
<main>
<h2 class="section-title">Overview</h2>
<section class="cards">
<article class="card"><div class="card-label">Active Connections</div><div class="card-value" id="active">—</div><div class="card-note">Established connections with a process ID</div></article>
<article class="card"><div class="card-label">Processes with Connections</div><div class="card-value" id="processes">—</div><div class="card-note">Unique process and PID pairs</div></article>
<article class="card"><div class="card-label">High-Risk Connections</div><div class="card-value" id="high">—</div><div class="card-note">HIGH risk heuristic findings</div></article>
<article class="card"><div class="card-label">Latest Snapshot</div><div class="card-value" id="snapshot-time" style="font-size:16px">Waiting</div><div class="card-note" id="network-note">No snapshot loaded yet</div></article>
</section>
<section class="panel"><div class="panel-header"><div><h2>Network Connections</h2><p>Connections collected by the local Security Shadow agent</p></div><span id="data-badge" class="badge medium">WAITING FOR DATA</span></div><div class="table-wrap"><table><thead><tr><th>PROCESS</th><th>PID</th><th>REMOTE ADDRESS</th><th>PORT</th><th>RISK</th><th>LEVEL</th><th>WHY FLAGGED</th></tr></thead><tbody id="connections"><tr><td colspan="7" class="empty">Start Security Shadow to populate this table.</td></tr></tbody></table></div></section>
<section class="panel"><div class="panel-header"><div><h2>Investigation Notes</h2><p>Heuristic signals are prompts for investigation, not proof of malicious activity</p></div></div><div id="alerts" class="empty">No snapshot received yet.</div></section>
</main><footer class="footer">Security Shadow · Local-only dashboard · Data is read from the local backend; no Google login is required.</footer>
<script>
const safe = value => String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[ch]);
function showEmpty(message){document.getElementById("connections").innerHTML=`<tr><td colspan="7" class="empty">${safe(message)}</td></tr>`;}
function getReasons(connection){if(Array.isArray(connection.reasons)&&connection.reasons.length){return connection.reasons.join("; ");}return "No configured heuristic was triggered";}
async function updateDashboard(){
 const status=document.getElementById("connection-status"), badge=document.getElementById("data-badge");
 try {
  const response=await fetch("/api/connections", {cache:"no-store"});
  const data=await response.json();
  if(!response.ok || !data.connected){
   status.textContent="● BACKEND NOT CONNECTED"; status.style.color="var(--red)";
   badge.textContent="NO LIVE DATA"; badge.className="badge high";
   showEmpty(data.message || "Backend unavailable. Start Security Shadow again.");
   document.getElementById("active").textContent="—";document.getElementById("processes").textContent="—";document.getElementById("high").textContent="—";
   document.getElementById("snapshot-time").textContent="Offline";document.getElementById("network-note").textContent="Check backend status";
   document.getElementById("alerts").textContent=data.message || "Backend unavailable.";return;
  }
  status.textContent="● LOCAL BACKEND CONNECTED";status.style.color="var(--green)";
  const conns=data.connections||[];
  if(!data.available){badge.textContent="WAITING FOR AGENT";badge.className="badge medium";showEmpty(data.message||"No agent snapshot has arrived yet.");document.getElementById("active").textContent="0";document.getElementById("processes").textContent="0";document.getElementById("high").textContent="0";document.getElementById("snapshot-time").textContent="Waiting";document.getElementById("network-note").textContent="Agent has not uploaded data";document.getElementById("alerts").textContent="No snapshot received yet.";return;}
  const processSet=new Set(conns.map(c=>`${c.process}:${c.pid}`));
  const high=conns.filter(c=>c.risk_level==="HIGH"||c.risk_level==="CRITICAL");
  document.getElementById("active").textContent=conns.length;document.getElementById("processes").textContent=processSet.size;document.getElementById("high").textContent=high.length;
  document.getElementById("snapshot-time").textContent=data.timestamp?new Date(data.timestamp).toLocaleTimeString():"Unknown";
  document.getElementById("network-note").textContent=data.network_note||`Updated ${new Date().toLocaleTimeString()}`;
  badge.textContent="LIVE SNAPSHOT";badge.className="badge low";
  document.getElementById("connections").innerHTML=conns.length?conns.map(c=>{const level=String(c.risk_level||"LOW").toLowerCase();return `<tr><td>${safe(c.process||"Unknown")}</td><td>${safe(c.pid??"—")}</td><td>${safe(c.remote_ip||"—")}</td><td>${safe(c.remote_port??"—")}</td><td>${safe(c.risk_score??0)}/100</td><td><span class="badge ${safe(level)}">${safe(c.risk_level||"LOW")}</span></td><td class="reason-cell">${safe(getReasons(c))}</td></tr>`}).join(""):`<tr><td colspan="7" class="empty">No established connections detected in this snapshot.</td></tr>`;
  const alerts=document.getElementById("alerts");
  if(!high.length){alerts.className="empty";alerts.textContent="No HIGH or CRITICAL connections in the current snapshot. LOW does not guarantee a connection is safe.";}
  else {alerts.className="";alerts.innerHTML=high.map(c=>`<div style="padding:14px 20px;border-bottom:1px solid var(--border)"><strong>${safe(c.process||"Unknown")}</strong> — ${safe(c.remote_ip||"—")}:${safe(c.remote_port??"—")} <span class="badge ${safe(String(c.risk_level||"HIGH").toLowerCase())}">${safe(c.risk_level||"HIGH")}</span><div style="color:var(--muted);margin-top:6px;font-size:12px">Score: ${safe(c.risk_score??0)}/100 · ${safe(getReasons(c))}</div></div>`).join("");}
 } catch(e){status.textContent="● DASHBOARD REQUEST FAILED";status.style.color="var(--red)";badge.textContent="REQUEST ERROR";badge.className="badge high";showEmpty("Could not retrieve backend data. Check that Security Shadow is running.");document.getElementById("alerts").textContent="Could not retrieve backend data.";console.error(e);}
}
updateDashboard();setInterval(updateDashboard,5000);
</script></body></html>"""


def read_read_token():
    try:
        token = READ_TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    return token if len(token) >= 32 else ""


@app.get("/")
def home():
    return render_template_string(DASHBOARD_HTML)


@app.get("/api/status")
def status():
    token = read_read_token()
    if not token:
        return jsonify({"status": "needs_setup", "message": "Run setup_local.py to create local credentials."}), 503
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/private/snapshot",
            headers={"Authorization": f"Bearer {token}"},
            timeout=2,
        )
    except requests.RequestException:
        return jsonify({"status": "backend_offline", "live_data_connected": False}), 503
    if response.status_code == 401:
        return jsonify({"status": "credential_rejected", "live_data_connected": False}), 503
    if not response.ok:
        return jsonify({"status": "backend_error", "live_data_connected": False}), 503
    try:
        available = bool(response.json().get("available"))
    except (ValueError, AttributeError):
        available = False
    return jsonify({
        "status": "running",
        "backend_reachable": True,
        "live_data_connected": available,
    })


@app.get("/api/connections")
def api_connections():
    token = read_read_token()
    if not token:
        return jsonify({"mode": "live_local", "connected": False, "message": "Local read credential missing or invalid. Run setup_local.py."}), 503
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/private/snapshot",
            headers={"Authorization": f"Bearer {token}"},
            timeout=3,
        )
    except requests.RequestException:
        return jsonify({"mode": "live_local", "connected": False, "message": "Private backend is offline. Start it with: python -m private_backend.app"}), 503

    if response.status_code == 401:
        return jsonify({"mode": "live_local", "connected": False, "message": "Read credential rejected. Run setup_local.py only if this is a fresh install; otherwise check token files."}), 503
    if not response.ok:
        return jsonify({"mode": "live_local", "connected": False, "message": f"Private backend returned HTTP {response.status_code}."}), 503

    try:
        result = response.json()
    except ValueError:
        return jsonify({"mode": "live_local", "connected": False, "message": "Private backend returned invalid JSON."}), 502

    if not result.get("available"):
        return jsonify({"mode": "live_local", "connected": True, "available": False, "message": result.get("message", "No snapshot received yet."), "connections": []})

    snapshot = result.get("snapshot") or {}
    computer_data = snapshot.get("computer_data") or {}
    connections = []
    for item in computer_data.get("connections") or []:
        connections.append({
            "process": item.get("process_name") or "Unknown",
            "pid": item.get("pid"),
            "remote_ip": item.get("remote_ip"),
            "remote_port": item.get("remote_port"),
            "risk_score": item.get("risk_score", 0),
            "risk_level": item.get("risk_level", "LOW"),
            "reasons": item.get("risk_reasons") or item.get("reasons") or [],
        })

    return jsonify({
        "mode": "live_local",
        "connected": True,
        "available": True,
        "timestamp": snapshot.get("timestamp"),
        "network_note": computer_data.get("network_note"),
        "connections": connections,
        "count": len(connections),
    })


if __name__ == "__main__":
    # Local personal monitoring only. Do not bind this dashboard publicly.
    app.run(host="127.0.0.1", port=int(os.getenv("SECURITY_SHADOW_DASHBOARD_PORT", "5000")), debug=False, use_reloader=False)

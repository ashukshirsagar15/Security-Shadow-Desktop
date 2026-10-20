"""Standalone Security Shadow desktop app (no separate browser window)."""
from __future__ import annotations

import logging
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import requests


# PyInstaller extracts bundled Python modules into _MEIPASS for a one-file build.
APP_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

LOCAL_APP_DATA = Path(
    os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
)
DATA_DIR = LOCAL_APP_DATA / "SecurityShadow"
PRIVATE_DIR = DATA_DIR / "private_backend"
TOKEN_FILE = PRIVATE_DIR / ".read_token"
LOG_FILE = DATA_DIR / "security_shadow.log"
BACKEND_URL = "http://127.0.0.1:5001"

DATA_DIR.mkdir(parents=True, exist_ok=True)
PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
os.environ["SECURITY_SHADOW_DATA_DIR"] = str(DATA_DIR)
os.environ["SECURITY_SHADOW_UPLOAD"] = "true"
os.environ["SECURITY_SHADOW_BACKEND_URL"] = BACKEND_URL

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


class SecurityShadowDesktop:
    def __init__(self, root: tk.Tk, backend_server, backend_thread, stop_event, agent_thread):
        self.root = root
        self.backend_server = backend_server
        self.backend_thread = backend_thread
        self.stop_event = stop_event
        self.agent_thread = agent_thread
        self.closed = False
        self.last_snapshot = None

        self.root.title("Security Shadow | Local Security Monitor")
        self.root.geometry("1380x850")
        self.root.minsize(980, 650)
        self.root.configure(bg="#0b1120")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self._configure_styles()
        self._build_ui()
        self.root.deiconify()
        self.root.after(800, self.refresh)

    def _configure_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "SS.Treeview",
            background="#111b2e",
            foreground="#e5edf8",
            fieldbackground="#111b2e",
            bordercolor="#24334a",
            rowheight=30,
            font=("Segoe UI", 9),
        )
        style.configure(
            "SS.Treeview.Heading",
            background="#1b2940",
            foreground="#b8c7dc",
            bordercolor="#24334a",
            relief="flat",
            font=("Segoe UI Semibold", 9),
        )
        style.map(
            "SS.Treeview",
            background=[("selected", "#245b50")],
            foreground=[("selected", "#ffffff")],
        )
        style.configure("SS.Vertical.TScrollbar", background="#1b2940", troughcolor="#0b1120")
        style.configure("SS.Horizontal.TScrollbar", background="#1b2940", troughcolor="#0b1120")

    def _build_ui(self):
        bg = "#0b1120"
        panel = "#111b2e"
        border = "#24334a"
        text = "#e5edf8"
        muted = "#8da2bd"
        green = "#4ade80"

        header = tk.Frame(self.root, bg=bg, padx=28, pady=22)
        header.pack(fill="x")
        tk.Label(header, text="SECURITY", font=("Segoe UI Semibold", 22), fg=text, bg=bg).pack(side="left")
        tk.Label(header, text=" SHADOW", font=("Segoe UI Semibold", 22), fg=green, bg=bg).pack(side="left")
        self.status_label = tk.Label(header, text="● STARTING LOCAL SERVICES", font=("Segoe UI Semibold", 10), fg="#facc15", bg=bg)
        self.status_label.pack(side="right", padx=(10, 0))
        tk.Label(
            self.root,
            text="LOCAL SECURITY MONITOR  •  DATA STAYS ON THIS COMPUTER  •  NO CLOUD ACCOUNT REQUIRED",
            font=("Segoe UI", 9), fg=muted, bg=bg, anchor="w",
        ).pack(fill="x", padx=30, pady=(0, 3))
        tk.Label(
            self.root,
            text="Developed by Ayush S. Kshirsagar",
            font=("Segoe UI", 9, "italic"), fg=muted, bg=bg, anchor="w",
        ).pack(fill="x", padx=30, pady=(0, 16))
        tk.Frame(self.root, bg=border, height=1).pack(fill="x")

        main = tk.Frame(self.root, bg=bg, padx=28, pady=20)
        main.pack(fill="both", expand=True)
        tk.Label(main, text="Overview", font=("Segoe UI Semibold", 14), fg=text, bg=bg).pack(anchor="w", pady=(0, 12))

        cards = tk.Frame(main, bg=bg)
        cards.pack(fill="x", pady=(0, 20))
        self.active_value = self._make_card(cards, "ACTIVE CONNECTIONS", "—", "Established connections")
        self.process_value = self._make_card(cards, "PROCESSES WITH CONNECTIONS", "—", "Unique process and PID pairs")
        self.high_value = self._make_card(cards, "HIGH-RISK FINDINGS", "—", "HIGH and CRITICAL heuristics")
        self.snapshot_value = self._make_card(cards, "LATEST SNAPSHOT", "Waiting", "Most recent collection time", compact=True)

        table_panel = tk.Frame(main, bg=panel, highlightbackground=border, highlightthickness=1)
        table_panel.pack(fill="both", expand=True)
        table_header = tk.Frame(table_panel, bg=panel, padx=16, pady=13)
        table_header.pack(fill="x")
        tk.Label(table_header, text="Network Connections", font=("Segoe UI Semibold", 12), fg=text, bg=panel).pack(side="left")
        tk.Label(table_header, text="Risk scores are heuristic indicators, not malware verdicts", font=("Segoe UI", 9), fg=muted, bg=panel).pack(side="right")

        columns = ("process", "pid", "remote", "port", "score", "level", "reasons")
        self.table = ttk.Treeview(table_panel, columns=columns, show="headings", style="SS.Treeview", selectmode="browse")
        headings = {
            "process": ("PROCESS", 170, "w"),
            "pid": ("PID", 70, "center"),
            "remote": ("REMOTE ADDRESS", 155, "w"),
            "port": ("PORT", 70, "center"),
            "score": ("RISK", 75, "center"),
            "level": ("LEVEL", 100, "center"),
            "reasons": ("WHY FLAGGED", 420, "w"),
        }
        for name, (label, width, anchor) in headings.items():
            self.table.heading(name, text=label)
            self.table.column(name, width=width, minwidth=55, anchor=anchor, stretch=name in {"process", "remote", "reasons"})
        self.table.tag_configure("LOW", foreground="#86efac")
        self.table.tag_configure("MEDIUM", foreground="#fde047")
        self.table.tag_configure("HIGH", foreground="#fca5a5")
        self.table.tag_configure("CRITICAL", foreground="#f87171")
        yscroll = ttk.Scrollbar(table_panel, orient="vertical", command=self.table.yview, style="SS.Vertical.TScrollbar")
        xscroll = ttk.Scrollbar(table_panel, orient="horizontal", command=self.table.xview, style="SS.Horizontal.TScrollbar")
        self.table.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.table.pack(fill="both", expand=True, padx=(12, 0), pady=(0, 0), side="left")
        yscroll.pack(fill="y", side="right")
        xscroll.pack(fill="x", side="bottom")
        self.table.bind("<<TreeviewSelect>>", self.show_selected_details)

        details = tk.Frame(main, bg=panel, highlightbackground=border, highlightthickness=1)
        details.pack(fill="x", pady=(14, 0))
        tk.Label(details, text="Investigation Notes", font=("Segoe UI Semibold", 11), fg=text, bg=panel, anchor="w").pack(fill="x", padx=14, pady=(10, 2))
        self.details_text = tk.Text(
            details, height=4, wrap="word", bg=panel, fg=muted,
            insertbackground=text, relief="flat", borderwidth=0,
            font=("Segoe UI", 9), padx=14, pady=4,
        )
        self.details_text.pack(fill="x")
        self.details_text.insert("1.0", "Waiting for the first local monitoring snapshot.")
        self.details_text.configure(state="disabled")

        footer = tk.Frame(self.root, bg=bg, padx=28, pady=10)
        footer.pack(fill="x")
        self.footer_label = tk.Label(footer, text=f"Local data folder: {DATA_DIR}", font=("Segoe UI", 8), fg=muted, bg=bg, anchor="w")
        self.footer_label.pack(side="left", fill="x", expand=True)
        tk.Button(footer, text="Refresh now", command=self.refresh, bg="#1f7666", fg="white", activebackground="#2c8a76", activeforeground="white", relief="flat", padx=16, pady=7, font=("Segoe UI Semibold", 9), cursor="hand2").pack(side="right")

    def _make_card(self, parent, title, value, note, compact=False):
        card = tk.Frame(parent, bg="#111b2e", padx=16, pady=14, highlightbackground="#24334a", highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=(0, 12))
        tk.Label(card, text=title, font=("Segoe UI", 8), fg="#8da2bd", bg="#111b2e", anchor="w").pack(fill="x")
        label = tk.Label(card, text=value, font=("Segoe UI Semibold", 23 if not compact else 13), fg="#e5edf8", bg="#111b2e", anchor="w")
        label.pack(fill="x", pady=(8, 5))
        tk.Label(card, text=note, font=("Segoe UI", 8), fg="#8da2bd", bg="#111b2e", anchor="w").pack(fill="x")
        return label

    def _set_details(self, content):
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", content)
        self.details_text.configure(state="disabled")

    @staticmethod
    def _format_time(value):
        if not value:
            return "Unknown"
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone().strftime("%H:%M:%S")
        except (ValueError, TypeError):
            return str(value)

    def refresh(self):
        if self.closed:
            return
        try:
            token = TOKEN_FILE.read_text(encoding="utf-8").strip()
            response = requests.get(
                f"{BACKEND_URL}/api/private/snapshot",
                headers={"Authorization": f"Bearer {token}"},
                timeout=1.5,
            )
            response.raise_for_status()
            result = response.json()
            self.status_label.configure(text="● LOCAL MONITORING ACTIVE", fg="#4ade80")

            if not result.get("available"):
                self.active_value.configure(text="0")
                self.process_value.configure(text="0")
                self.high_value.configure(text="0")
                self.snapshot_value.configure(text="Waiting")
                self._replace_rows([])
                self._set_details("Waiting for the first monitoring snapshot. The agent collects process and network information every 5 seconds.")
            else:
                snapshot = result.get("snapshot") or {}
                computer_data = snapshot.get("computer_data") or {}
                connections = computer_data.get("connections") or []
                process_set = {(item.get("process_name", "Unknown"), item.get("pid")) for item in connections}
                high_count = sum(item.get("risk_level") in {"HIGH", "CRITICAL"} for item in connections)
                self.active_value.configure(text=str(len(connections)))
                self.process_value.configure(text=str(len(process_set)))
                self.high_value.configure(text=str(high_count), fg="#f87171" if high_count else "#e5edf8")
                self.snapshot_value.configure(text=self._format_time(snapshot.get("timestamp")))
                self._replace_rows(connections)
                note = computer_data.get("network_note")
                intro = f"Latest snapshot: {self._format_time(snapshot.get('timestamp'))}. {len(connections)} established connection(s) were assessed."
                if note:
                    intro += f"\nCollection note: {note}"
                intro += "\nHeuristic results are prompts for investigation, not proof that a connection is malicious. A LOW score does not guarantee safety."
                self._set_details(intro)
                self.last_snapshot = snapshot
        except (OSError, requests.RequestException, ValueError) as exc:
            self.status_label.configure(text="● LOCAL SERVICE CONNECTING", fg="#facc15")
            logging.warning("Dashboard refresh failed: %s", type(exc).__name__)
            self._set_details("The local monitoring service is starting or temporarily unavailable. If this continues, close and reopen Security Shadow. See the local log file for details.")
        if not self.closed:
            self.root.after(2000, self.refresh)

    def _replace_rows(self, connections):
        for row in self.table.get_children():
            self.table.delete(row)
        for index, item in enumerate(connections):
            level = str(item.get("risk_level") or "LOW").upper()
            reasons = item.get("risk_reasons") or item.get("reasons") or ["No configured heuristic was triggered"]
            if not isinstance(reasons, list):
                reasons = [str(reasons)]
            reason_text = "; ".join(str(reason) for reason in reasons)
            self.table.insert(
                "", "end", iid=str(index),
                values=(
                    item.get("process_name") or "Unknown",
                    item.get("pid") if item.get("pid") is not None else "—",
                    item.get("remote_ip") or "—",
                    item.get("remote_port") if item.get("remote_port") is not None else "—",
                    f"{item.get('risk_score', 0)}/100",
                    level,
                    reason_text,
                ),
                tags=(level if level in {"LOW", "MEDIUM", "HIGH", "CRITICAL"} else "LOW",),
            )

    def show_selected_details(self, _event=None):
        selected = self.table.selection()
        if not selected or not self.last_snapshot:
            return
        try:
            item = (self.last_snapshot.get("computer_data") or {}).get("connections", [])[int(selected[0])]
        except (IndexError, ValueError, TypeError):
            return
        reasons = item.get("risk_reasons") or item.get("reasons") or ["No configured heuristic was triggered"]
        detail = (
            f"Process: {item.get('process_name') or 'Unknown'}  |  PID: {item.get('pid') or 'Unknown'}\n"
            f"Remote endpoint: {item.get('remote_ip') or 'Unknown'}:{item.get('remote_port') or 'Unknown'}\n"
            f"Risk assessment: {item.get('risk_score', 0)}/100 — {item.get('risk_level', 'LOW')}\n"
            f"Signals: {'; '.join(str(reason) for reason in reasons)}\n"
            "These are heuristic signals for investigation, not proof of malicious activity."
        )
        self._set_details(detail)

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.status_label.configure(text="● STOPPING LOCAL SERVICES", fg="#facc15")
        self.stop_event.set()
        try:
            self.backend_server.shutdown()
            self.backend_server.server_close()
        except Exception:
            logging.exception("Error while stopping backend server")
        self.root.destroy()


def main() -> int:
    root = tk.Tk()
    root.withdraw()
    try:
        from setup_local import main as prepare_credentials
        prepare_credentials()

        from private_backend.app import app as backend_app
        from werkzeug.serving import make_server
        from agent.agent import run_agent_loop

        server = make_server("127.0.0.1", 5001, backend_app, threaded=True)
        server_thread = threading.Thread(target=server.serve_forever, name="SecurityShadowBackend", daemon=True)
        server_thread.start()

        stop_event = threading.Event()
        agent_thread = threading.Thread(
            target=run_agent_loop,
            kwargs={"stop_event": stop_event, "log_callback": logging.info},
            name="SecurityShadowAgent",
            daemon=True,
        )
        agent_thread.start()

        SecurityShadowDesktop(root, server, server_thread, stop_event, agent_thread)
        root.mainloop()
        return 0
    except Exception as exc:
        logging.exception("Security Shadow failed to start")
        messagebox.showerror(
            "Security Shadow could not start",
            "Security Shadow could not start its local services.\n\n"
            f"Reason: {exc}\n\n"
            f"Diagnostic log: {LOG_FILE}\n\n"
            "Close any other copy of Security Shadow and try again.",
            parent=root,
        )
        try:
            root.destroy()
        except tk.TclError:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

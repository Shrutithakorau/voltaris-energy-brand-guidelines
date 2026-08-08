"""
Voltaris Energy Lead API + static file server.
Stores leads in SQLite (data/leads.db).
"""

from __future__ import annotations

import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "leads.db"
HOST = "127.0.0.1"
PORT = 8787

PRODUCT_TYPES = {"solar", "battery", "solar-battery"}
PHASES = {"single", "three"}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                mobile TEXT NOT NULL,
                email TEXT NOT NULL,
                address TEXT NOT NULL,
                product_type TEXT NOT NULL,
                nmi TEXT,
                phase TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC)"
        )
        conn.commit()


def row_to_lead(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "customerName": row["customer_name"],
        "mobile": row["mobile"],
        "email": row["email"],
        "address": row["address"],
        "productType": row["product_type"],
        "nmi": row["nmi"] or "",
        "phase": row["phase"],
        "createdAt": row["created_at"],
    }


def validate_lead(payload: dict) -> tuple[dict | None, str | None]:
    if not isinstance(payload, dict):
        return None, "Invalid JSON body."

    customer_name = str(payload.get("customerName", "")).strip()
    mobile = str(payload.get("mobile", "")).strip()
    email = str(payload.get("email", "")).strip()
    address = str(payload.get("address", "")).strip()
    product_type = str(payload.get("productType", "")).strip()
    nmi = str(payload.get("nmi", "")).strip().upper()
    phase = str(payload.get("phase", "")).strip()

    if not customer_name:
        return None, "Customer name is required."
    if not mobile:
        return None, "Mobile number is required."
    if not email or not EMAIL_RE.match(email):
        return None, "A valid email address is required."
    if not address:
        return None, "Address is required."
    if product_type not in PRODUCT_TYPES:
        return None, "Product type must be solar, battery, or solar-battery."
    if phase not in PHASES:
        return None, "Phase must be single or three."
    if nmi and (len(nmi) > 11 or not re.match(r"^[A-Z0-9]+$", nmi)):
        return None, "NMI must be up to 11 letters/numbers."

    return {
        "customer_name": customer_name,
        "mobile": mobile,
        "email": email,
        "address": address,
        "product_type": product_type,
        "nmi": nmi or None,
        "phase": phase,
    }, None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def _json(self, status: int, payload: dict | list):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._json(200, {"ok": True, "database": str(DB_PATH)})
            return

        if parsed.path == "/api/leads":
            q = (parse_qs(parsed.query).get("q") or [""])[0].strip().lower()
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM leads ORDER BY datetime(created_at) DESC"
                ).fetchall()
            leads = [row_to_lead(r) for r in rows]
            if q:
                leads = [
                    l
                    for l in leads
                    if q
                    in " ".join(
                        [
                            l["customerName"],
                            l["mobile"],
                            l["email"],
                            l["address"],
                            l["nmi"],
                            l["productType"],
                            l["phase"],
                        ]
                    ).lower()
                ]
            self._json(200, {"leads": leads, "count": len(leads)})
            return

        if parsed.path in ("/", "/leads", "/leads/"):
            self.path = "/leads.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/leads":
            self._json(404, {"error": "Not found"})
            return

        try:
            payload = self._read_json()
        except json.JSONDecodeError:
            self._json(400, {"error": "Invalid JSON"})
            return

        data, err = validate_lead(payload)
        if err:
            self._json(400, {"error": err})
            return

        lead_id = "lead_" + uuid.uuid4().hex[:12]
        created_at = utc_now()
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO leads (
                    id, customer_name, mobile, email, address,
                    product_type, nmi, phase, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lead_id,
                    data["customer_name"],
                    data["mobile"],
                    data["email"],
                    data["address"],
                    data["product_type"],
                    data["nmi"],
                    data["phase"],
                    created_at,
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM leads WHERE id = ?", (lead_id,)
            ).fetchone()

        self._json(201, {"lead": row_to_lead(row)})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if len(parts) != 3 or parts[0] != "api" or parts[1] != "leads":
            self._json(404, {"error": "Not found"})
            return

        lead_id = parts[2]
        with get_conn() as conn:
            cur = conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
            conn.commit()
            deleted = cur.rowcount

        if not deleted:
            self._json(404, {"error": "Lead not found"})
            return
        self._json(200, {"ok": True, "id": lead_id})

    def log_message(self, fmt: str, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


def main():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("Voltaris Lead Manager")
    print(f"  App:      http://{HOST}:{PORT}/leads.html")
    print(f"  API:      http://{HOST}:{PORT}/api/leads")
    print(f"  Database: {DB_PATH}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()

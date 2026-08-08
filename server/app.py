"""
Voltaris Energy Lead API + static file server.
Stores leads and notes in SQLite (data/leads.db).
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
STATUSES = {
    "lead",
    "opportunity",
    "quoted",
    "closed_won",
    "closed_lost",
    "installation",
}
# Notes allowed once a record has progressed to opportunity or beyond
NOTE_STATUSES = {
    "opportunity",
    "quoted",
    "closed_won",
    "closed_lost",
    "installation",
}

# Strict pipeline: lead -> opportunity -> quoted -> closed_won|closed_lost -> installation (from won)
ALLOWED_TRANSITIONS = {
    "lead": {"opportunity"},
    "opportunity": {"quoted"},
    "quoted": {"closed_won", "closed_lost"},
    "closed_won": {"installation"},
    "closed_lost": set(),
    "installation": set(),
}
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
                status TEXT NOT NULL DEFAULT 'lead',
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
            """
        )
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(leads)").fetchall()}
        if "status" not in cols:
            conn.execute(
                "ALTER TABLE leads ADD COLUMN status TEXT NOT NULL DEFAULT 'lead'"
            )
        if "updated_at" not in cols:
            conn.execute("ALTER TABLE leads ADD COLUMN updated_at TEXT")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                lead_id TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_notes_lead_id ON notes(lead_id, created_at DESC)"
        )
        conn.commit()


def normalize_status(status: str) -> str:
    status = (status or "lead").strip().lower()
    if status == "closed_won":
        return "installation"
    return status


def row_to_lead(row: sqlite3.Row) -> dict:
    keys = row.keys()
    return {
        "id": row["id"],
        "customerName": row["customer_name"],
        "mobile": row["mobile"],
        "email": row["email"],
        "address": row["address"],
        "productType": row["product_type"],
        "nmi": row["nmi"] or "",
        "phase": row["phase"],
        "status": row["status"] if "status" in keys else "lead",
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"] if "updated_at" in keys else None,
    }


def row_to_note(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "leadId": row["lead_id"],
        "body": row["body"],
        "createdAt": row["created_at"],
    }


def get_lead(conn: sqlite3.Connection, lead_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()


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
    status = str(payload.get("status", "lead")).strip().lower() or "lead"

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
    if status not in STATUSES:
        return None, "Invalid status."

    status = normalize_status(status)

    return {
        "customer_name": customer_name,
        "mobile": mobile,
        "email": email,
        "address": address,
        "product_type": product_type,
        "nmi": nmi or None,
        "phase": phase,
        "status": status,
    }, None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
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
        path = parsed.path

        if path == "/api/health":
            self._json(200, {"ok": True, "database": str(DB_PATH)})
            return

        # GET /api/leads/:id/notes
        parts = path.strip("/").split("/")
        if (
            len(parts) == 4
            and parts[0] == "api"
            and parts[1] == "leads"
            and parts[3] == "notes"
        ):
            lead_id = parts[2]
            with get_conn() as conn:
                lead = get_lead(conn, lead_id)
                if not lead:
                    self._json(404, {"error": "Lead not found"})
                    return
                rows = conn.execute(
                    """
                    SELECT * FROM notes
                    WHERE lead_id = ?
                    ORDER BY datetime(created_at) DESC
                    """,
                    (lead_id,),
                ).fetchall()
            self._json(
                200,
                {
                    "lead": row_to_lead(lead),
                    "notes": [row_to_note(r) for r in rows],
                    "count": len(rows),
                },
            )
            return

        # GET /api/leads/:id
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "leads":
            lead_id = parts[2]
            with get_conn() as conn:
                lead = get_lead(conn, lead_id)
            if not lead:
                self._json(404, {"error": "Lead not found"})
                return
            self._json(200, {"lead": row_to_lead(lead)})
            return

        if path == "/api/leads":
            qs = parse_qs(parsed.query)
            q = (qs.get("q") or [""])[0].strip().lower()
            status_filter = (qs.get("status") or [""])[0].strip().lower()
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM leads ORDER BY datetime(created_at) DESC"
                ).fetchall()
            leads = [row_to_lead(r) for r in rows]
            if status_filter and status_filter != "all":
                leads = [l for l in leads if l["status"] == status_filter]
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
                            l["status"],
                        ]
                    ).lower()
                ]
            self._json(200, {"leads": leads, "count": len(leads)})
            return

        if path in ("/", "/leads", "/leads/"):
            self.path = "/leads.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        parts = path.strip("/").split("/")

        # POST /api/leads/:id/notes
        if (
            len(parts) == 4
            and parts[0] == "api"
            and parts[1] == "leads"
            and parts[3] == "notes"
        ):
            lead_id = parts[2]
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._json(400, {"error": "Invalid JSON"})
                return

            body = str(payload.get("body", "")).strip()
            if not body:
                self._json(400, {"error": "Note text is required."})
                return
            if len(body) > 5000:
                self._json(400, {"error": "Note is too long (max 5000 characters)."})
                return

            with get_conn() as conn:
                lead = get_lead(conn, lead_id)
                if not lead:
                    self._json(404, {"error": "Lead not found"})
                    return
                status = lead["status"]
                if status not in NOTE_STATUSES:
                    self._json(
                        400,
                        {
                            "error": "Move this record to Opportunity before adding notes."
                        },
                    )
                    return

                note_id = "note_" + uuid.uuid4().hex[:12]
                created_at = utc_now()
                conn.execute(
                    """
                    INSERT INTO notes (id, lead_id, body, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (note_id, lead_id, body, created_at),
                )
                conn.execute(
                    "UPDATE leads SET updated_at = ? WHERE id = ?",
                    (created_at, lead_id),
                )
                conn.commit()
                row = conn.execute(
                    "SELECT * FROM notes WHERE id = ?", (note_id,)
                ).fetchone()

            self._json(201, {"note": row_to_note(row)})
            return

        if path != "/api/leads":
            self._json(404, {"error": "Not found"})
            return

        try:
            payload = self._read_json()
        except json.JSONDecodeError:
            self._json(400, {"error": "Invalid JSON"})
            return

        if "status" not in payload:
            payload["status"] = "lead"

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
                    product_type, nmi, phase, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    data["status"],
                    created_at,
                    created_at,
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM leads WHERE id = ?", (lead_id,)
            ).fetchone()

        self._json(201, {"lead": row_to_lead(row)})

    def do_PATCH(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if len(parts) != 3 or parts[0] != "api" or parts[1] != "leads":
            self._json(404, {"error": "Not found"})
            return

        lead_id = parts[2]
        try:
            payload = self._read_json()
        except json.JSONDecodeError:
            self._json(400, {"error": "Invalid JSON"})
            return

        with get_conn() as conn:
            existing = get_lead(conn, lead_id)
            if not existing:
                self._json(404, {"error": "Lead not found"})
                return

            current = row_to_lead(existing)
            current_status = current["status"]
            requested_status = str(
                payload.get("status", current_status)
            ).strip().lower()

            if requested_status not in STATUSES:
                self._json(400, {"error": "Invalid status."})
                return

            # Enforce sequential workflow when status changes
            if requested_status != current_status:
                allowed = ALLOWED_TRANSITIONS.get(current_status, set())
                # closed_won is requested by user but stored as installation
                if requested_status == "closed_won":
                    if "closed_won" not in allowed and "installation" not in allowed:
                        # quoted can go to closed_won
                        if "closed_won" not in allowed:
                            self._json(
                                400,
                                {
                                    "error": f"Cannot move from {current_status} to closed_won. Follow the pipeline."
                                },
                            )
                            return
                elif requested_status not in allowed:
                    # Allow no-op already handled; installation may come from closed_won normalize
                    if not (
                        requested_status == "installation"
                        and current_status == "quoted"
                        and "closed_won" in allowed
                    ):
                        next_steps = ", ".join(sorted(allowed)) or "none"
                        self._json(
                            400,
                            {
                                "error": f"Invalid step. From {current_status} you can only move to: {next_steps}."
                            },
                        )
                        return

            # Merge: allow status-only updates or full field updates
            merged = {
                "customerName": payload.get("customerName", current["customerName"]),
                "mobile": payload.get("mobile", current["mobile"]),
                "email": payload.get("email", current["email"]),
                "address": payload.get("address", current["address"]),
                "productType": payload.get("productType", current["productType"]),
                "nmi": payload.get("nmi", current["nmi"]),
                "phase": payload.get("phase", current["phase"]),
                "status": requested_status,
            }

            data, err = validate_lead(merged)
            if err:
                self._json(400, {"error": err})
                return

            final_status = data["status"]
            updated_at = utc_now()

            conn.execute(
                """
                UPDATE leads SET
                    customer_name = ?, mobile = ?, email = ?, address = ?,
                    product_type = ?, nmi = ?, phase = ?, status = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    data["customer_name"],
                    data["mobile"],
                    data["email"],
                    data["address"],
                    data["product_type"],
                    data["nmi"],
                    data["phase"],
                    final_status,
                    updated_at,
                    lead_id,
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM leads WHERE id = ?", (lead_id,)
            ).fetchone()

        self._json(
            200,
            {
                "lead": row_to_lead(row),
                "movedToInstallation": requested_status == "closed_won",
                "openedNotes": final_status in NOTE_STATUSES,
            },
        )

    def do_DELETE(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if len(parts) != 3 or parts[0] != "api" or parts[1] != "leads":
            self._json(404, {"error": "Not found"})
            return

        lead_id = parts[2]
        with get_conn() as conn:
            conn.execute("DELETE FROM notes WHERE lead_id = ?", (lead_id,))
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

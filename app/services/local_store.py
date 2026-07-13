"""SQLite storage backend for the single-container appliance profile.

Uses only the Python standard library, so the appliance image carries no
database server and no extra dependencies (smaller scan/SBOM surface for
accreditation). Selected when DATABASE_URL starts with "sqlite:", e.g.
sqlite:////data/harness.db (absolute) or sqlite:///harness.db (relative).
"""

import sqlite3
import threading
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id            TEXT PRIMARY KEY,
    tenant_id     TEXT NOT NULL,
    source        TEXT NOT NULL,
    content       TEXT NOT NULL,
    content_hash  TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    UNIQUE (tenant_id, content_hash)
);
CREATE INDEX IF NOT EXISTS idx_documents_tenant ON documents (tenant_id);

CREATE TABLE IF NOT EXISTS audit_events (
    id               TEXT PRIMARY KEY,
    actor            TEXT NOT NULL,
    action           TEXT NOT NULL,
    resource_type    TEXT NOT NULL,
    resource_id      TEXT,
    tenant_id        TEXT,
    policy_decision  TEXT NOT NULL,
    reason           TEXT,
    created_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_events_tenant ON audit_events (tenant_id);
"""

_init_lock = threading.Lock()
_initialized: set[str] = set()


def is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite:")


def _path_from_url(database_url: str) -> str:
    # sqlite:///relative.db -> relative.db ; sqlite:////data/h.db -> /data/h.db
    tail = database_url.split("://", 1)[1]
    return tail[1:] if tail.startswith("/") else tail


def connect(database_url: str) -> sqlite3.Connection:
    """Open a connection, creating the file and schema on first use."""
    path = _path_from_url(database_url)
    parent = Path(path).parent
    if str(parent) not in ("", "."):
        parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    with _init_lock:
        if path not in _initialized:
            conn.executescript(_SCHEMA)
            conn.commit()
            _initialized.add(path)
    return conn

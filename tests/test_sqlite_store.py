import sqlite3

import pytest

from app.services import audit_service, retrieval_service
from app.settings import get_settings


@pytest.fixture
def sqlite_db(tmp_path, monkeypatch):
    db_path = tmp_path / "harness.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    get_settings.cache_clear()
    yield db_path
    get_settings.cache_clear()


def test_ingest_and_retrieve_via_sqlite(sqlite_db):
    document = retrieval_service.ingest_text(
        tenant_id="tenant-a",
        source="synthetic-handbook",
        text="Demo agencies process permit applications within ten business days.",
    )
    results = retrieval_service.retrieve(tenant_id="tenant-a", query="permit")
    assert results
    assert results[0]["document_id"] == document["id"]
    assert results[0]["citation"].startswith("synthetic-handbook#")

    # Tenant isolation holds in the sqlite backend too.
    assert retrieval_service.retrieve(tenant_id="tenant-b", query="permit") == []

    with sqlite3.connect(sqlite_db) as conn:
        count = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
    assert count == 1


def test_duplicate_ingest_is_idempotent(sqlite_db):
    for _ in range(2):
        retrieval_service.ingest_text(
            tenant_id="tenant-a", source="synthetic-handbook", text="same synthetic text"
        )
    with sqlite3.connect(sqlite_db) as conn:
        count = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
    assert count == 1


def test_audit_events_written_to_sqlite(sqlite_db):
    audit_service.record(
        actor="pytest",
        action="chat",
        resource_type="model",
        tenant_id="tenant-a",
        policy_decision="deny",
        reason="blocked by clean-room rule",
    )
    with sqlite3.connect(sqlite_db) as conn:
        rows = conn.execute(
            "SELECT actor, action, policy_decision FROM audit_events"
        ).fetchall()
    assert rows == [("pytest", "chat", "deny")]

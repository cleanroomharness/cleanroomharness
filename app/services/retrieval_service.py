"""Retrieval service.

Stores demo documents with tenant ID, source metadata, and a content hash, and
performs simple keyword retrieval with citations. The documents table already
carries an embedding column (pgvector) so vector search can be added without a
schema change. Falls back to an in-memory store when Postgres is unreachable
so the demo endpoints work without the full stack.
"""

import hashlib
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from app.settings import get_settings

logger = logging.getLogger("cleanroom.retrieval")

_db_available: bool | None = None
_memory_store: list[dict[str, Any]] = []


def ingest_text(*, tenant_id: str, source: str, text: str) -> dict[str, Any]:
    document = {
        "id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "source": source,
        "content": text,
        "content_hash": hashlib.sha256(text.encode()).hexdigest(),
        "created_at": datetime.now(UTC).isoformat(),
    }
    if not _insert_db(document):
        _memory_store.append(document)
    return {k: v for k, v in document.items() if k != "content"}


def retrieve(*, tenant_id: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    results = _search_db(tenant_id=tenant_id, query=query, top_k=top_k)
    if results is None:
        results = [
            doc
            for doc in _memory_store
            if doc["tenant_id"] == tenant_id and query.lower() in doc["content"].lower()
        ][:top_k]
    return [
        {
            "document_id": doc["id"],
            "source": doc["source"],
            "snippet": _snippet(doc["content"], query),
            "content_hash": doc["content_hash"],
            "citation": f"{doc['source']}#{doc['content_hash'][:12]}",
        }
        for doc in results
    ]


def _snippet(content: str, query: str, width: int = 240) -> str:
    index = content.lower().find(query.lower())
    start = max(index - width // 2, 0) if index >= 0 else 0
    return content[start : start + width]


def _insert_db(document: dict[str, Any]) -> bool:
    global _db_available
    if _db_available is False:
        return False
    try:
        import psycopg

        with psycopg.connect(get_settings().database_url, connect_timeout=2) as conn:
            conn.execute(
                """
                INSERT INTO documents
                    (id, tenant_id, source, content, content_hash, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (tenant_id, content_hash) DO NOTHING
                """,
                (
                    document["id"],
                    document["tenant_id"],
                    document["source"],
                    document["content"],
                    document["content_hash"],
                    document["created_at"],
                ),
            )
        _db_available = True
        return True
    except Exception:  # noqa: BLE001 - degrade to in-memory demo mode
        _note_db_down()
        return False


def _search_db(*, tenant_id: str, query: str, top_k: int) -> list[dict[str, Any]] | None:
    global _db_available
    if _db_available is False:
        return None
    try:
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(
            get_settings().database_url, connect_timeout=2, row_factory=dict_row
        ) as conn:
            rows = conn.execute(
                """
                SELECT id, tenant_id, source, content, content_hash
                FROM documents
                WHERE tenant_id = %s AND content ILIKE %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (tenant_id, f"%{query}%", top_k),
            ).fetchall()
        _db_available = True
        return [dict(row) for row in rows]
    except Exception:  # noqa: BLE001 - degrade to in-memory demo mode
        _note_db_down()
        return None


def _note_db_down() -> None:
    global _db_available
    if _db_available is None:
        logger.warning("retrieval database unavailable; using in-memory demo store")
    _db_available = False

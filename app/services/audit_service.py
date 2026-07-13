"""Audit events.

Every model call, ingest, retrieval, and tool dry run can record an audit
event. Events go to the audit_events table in Postgres when available; if the
database is unreachable (e.g. unit tests, degraded mode) they fall back to
structured logs so the trail is never silently dropped.
"""

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from app.settings import get_settings

logger = logging.getLogger("cleanroom.audit")

_db_available: bool | None = None

_INSERT = """
INSERT INTO audit_events
    (id, actor, action, resource_type, resource_id, tenant_id,
     policy_decision, reason, created_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def record(
    *,
    actor: str,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    tenant_id: str | None = None,
    policy_decision: str = "allow",
    reason: str = "",
) -> dict[str, Any]:
    event = {
        "id": str(uuid.uuid4()),
        "actor": actor,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "tenant_id": tenant_id,
        "policy_decision": policy_decision,
        "reason": reason,
        "created_at": datetime.now(UTC).isoformat(),
    }
    if not _write_db(event):
        logger.info("audit_event %s", json.dumps(event))
    return event


def _write_db(event: dict[str, Any]) -> bool:
    global _db_available
    if _db_available is False:
        return False
    try:
        import psycopg

        with psycopg.connect(get_settings().database_url, connect_timeout=2) as conn:
            conn.execute(
                _INSERT,
                (
                    event["id"],
                    event["actor"],
                    event["action"],
                    event["resource_type"],
                    event["resource_id"],
                    event["tenant_id"],
                    event["policy_decision"],
                    event["reason"],
                    event["created_at"],
                ),
            )
        _db_available = True
        return True
    except Exception:  # noqa: BLE001 - audit must never take the API down
        if _db_available is None:
            logger.warning("audit database unavailable; falling back to log output")
        _db_available = False
        return False

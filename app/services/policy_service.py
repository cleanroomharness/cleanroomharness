"""Policy gate.

Runs before model calls, ingestion, retrieval, and tool use. The initial
rules are simple pattern guardrails; the interface (evaluate -> PolicyDecision)
is stable so real classifiers, PII/PHI/CUI detectors, and data-boundary checks
can be added without changing callers.
"""

import re
from dataclasses import dataclass
from enum import StrEnum


class PolicyAction(StrEnum):
    MODEL_CALL = "model_call"
    INGEST = "ingest"
    RETRIEVE = "retrieve"
    TOOL_DRY_RUN = "tool_dry_run"
    TOOL_EXECUTE = "tool_execute"


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    action: PolicyAction
    reason: str
    matched_rule: str | None = None


# Clean-room guardrails: each rule is (name, pattern). Deliberately blunt —
# they exist to catch obvious boundary violations, not to be exhaustive.
_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "no-customer-data-export",
        re.compile(r"export\s+(?:all\s+)?(?:customer|case|call|claim)\s+data", re.I),
    ),
    ("no-proprietary-prompts", re.compile(r"proprietary\s+prompts?", re.I)),
    (
        "no-employer-code-reuse",
        re.compile(
            r"(?:copy|paste|reuse)\b.{0,40}\b(?:employer|internal|proprietary)\s+(?:code|source)",
            re.I,
        ),
    ),
    (
        "no-confidential-content",
        re.compile(r"\b(?:confidential|internal[- ]only|do not distribute)\b", re.I),
    ),
    (
        "no-credentials-in-payloads",
        re.compile(
            r"\b(?:api[_ -]?key|password|credential|access[_ -]?token|private[_ -]?key)\b",
            re.I,
        ),
    ),
]


def evaluate(
    action: PolicyAction,
    content: str,
    context: dict | None = None,
) -> PolicyDecision:
    """Evaluate an action + payload against the clean-room rules."""
    context = context or {}

    for rule_name, pattern in _RULES:
        if pattern.search(content or ""):
            return PolicyDecision(
                allowed=False,
                action=action,
                reason=f"blocked by clean-room rule '{rule_name}'",
                matched_rule=rule_name,
            )

    if action is PolicyAction.TOOL_EXECUTE and not context.get("approved_by"):
        return PolicyDecision(
            allowed=False,
            action=action,
            reason="side-effecting tools require human approval (approved_by)",
            matched_rule="human-approval-required",
        )

    return PolicyDecision(allowed=True, action=action, reason="no policy rule matched")

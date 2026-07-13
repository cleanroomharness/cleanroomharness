"""Evaluation service.

Loads synthetic eval cases (evals/synthetic_cases.jsonl) and scores model
outputs against the eval contract: expected substrings must appear, forbidden
substrings must not. Only synthetic data — never employer data.
"""

import json
from pathlib import Path
from typing import Any

DEFAULT_CASES_PATH = Path(__file__).resolve().parents[2] / "evals" / "synthetic_cases.jsonl"


def load_cases(path: Path = DEFAULT_CASES_PATH) -> list[dict[str, Any]]:
    cases = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def score_output(case: dict[str, Any], output: str) -> dict[str, Any]:
    lowered = output.lower()
    missing = [
        expected
        for expected in case.get("expected_contains", [])
        if expected.lower() not in lowered
    ]
    forbidden = [
        banned
        for banned in case.get("forbidden_contains", [])
        if banned.lower() in lowered
    ]
    return {
        "task": case.get("task"),
        "passed": not missing and not forbidden,
        "missing_expected": missing,
        "forbidden_found": forbidden,
        "needs_human_review": bool(forbidden),
    }

# Evaluations

Synthetic evaluation cases and the contract they follow. No employer data,
no real customer content — every case here is invented.

- [eval_contract.md](eval_contract.md) — what every eval must define.
- [synthetic_cases.jsonl](synthetic_cases.jsonl) — starter cases, one JSON object per line.

`app/services/evaluation_service.py` loads these cases and scores outputs:
expected substrings must appear, forbidden substrings must not.

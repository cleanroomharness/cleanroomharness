# Policies

Operational policies enforced (or referenced) by the policy gate
(`app/services/policy_service.py`).

- [clean_room_policy.md](clean_room_policy.md) — operational summary of the clean-room rules the gate enforces. The full governance version lives in [../governance/clean_room_policy.md](../governance/clean_room_policy.md).
- [data_boundary_policy.md](data_boundary_policy.md) — what data may enter the system and where it may flow.

When you extend the policy gate, document the rule here and add a test in `tests/test_policy.py`.

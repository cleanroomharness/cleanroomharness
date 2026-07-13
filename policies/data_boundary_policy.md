# Data Boundary Policy

## Public repo (this repository)

- Synthetic and generalized content only.
- No real customer, employee, case, call, or claim data — ever.
- No credentials or keys; `.env` is git-ignored and `make check` scans for secret-like artifacts.

## Runtime boundaries

1. **Tenant isolation.** Every document and audit event carries a `tenant_id`. Queries filter by tenant. Cross-tenant retrieval is a policy violation.
2. **Model boundary.** Data leaves the system only through the LiteLLM gateway to endpoints listed in `infra/litellm/config.yaml`. Restrict that list per deployment (approved regions, on-prem only for air-gapped work).
3. **Tool boundary.** Tools receive validated arguments only. Side effects require `TOOLS_EXECUTION_ENABLED=true` plus a named `approved_by`.
4. **Telemetry boundary.** Logs, traces, and audit events carry identifiers and decisions — never raw payloads, prompts containing sensitive data, or secrets.
5. **Company boundary.** Data, prompts, code, and configuration never move between company deployments. Each company runs its own private fork with its own storage.

## Classification hooks

`app/services/policy_service.py` is the single choke point. Add per-deployment
classifiers (PII/PHI/CUI detection, DLP, regex packs) there so every model
call, ingest, retrieval, and tool call inherits them.

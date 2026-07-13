# Risk Register

| ID | Risk | Description | Likelihood | Impact | Mitigations |
|----|------|-------------|------------|--------|-------------|
| R1 | Data leakage | Employer or customer data enters the public repo, a prompt, or another company's environment. | Medium | Critical | Clean-room policy; `make check` in CI; synthetic-data-only rule; policy gate blocks obvious payloads. |
| R2 | Prompt leakage | Proprietary prompts are reused across companies or committed publicly. | Medium | High | Prompts directory holds portable prompts only; policy gate flags "proprietary prompt" payloads; review before commit. |
| R3 | Tool overreach | A tool performs side effects beyond what was requested or approved. | Medium | High | Dry-run-first contract; execution disabled by default; human approval required; audit_events trail. |
| R4 | Hallucinated actions | The model asserts an action happened that never did, or invents citations. | Medium | High | Tools report actual results; retrieval returns real citations; eval contract includes forbidden outputs. |
| R5 | PII/PHI/CUI mishandling | Regulated data is ingested, logged, or sent to an unapproved model endpoint. | Medium | Critical | Policy gate hook for data classification; no sensitive payloads in logs/traces; approved-endpoint lists per deployment. |
| R6 | Timekeeping conflict | Work on this harness overlaps with employer time or equipment. | Medium | High | Work on personal time and equipment; keep written approval where required; decision log records provenance. |
| R7 | Organizational conflict of interest | Serving multiple companies in the same market creates a real or perceived conflict. | Low | High | Disclose engagements as contracts require; per-company repos; no cross-company information flow. |
| R8 | Unclear IP ownership | Ambiguity over whether a contribution belongs to an employer. | Medium | High | Only generalized patterns in public; explicit release approval for anything created on employer time; Apache-2.0 licensing. |

Review this register at the start of each engagement and record changes in the decision log.

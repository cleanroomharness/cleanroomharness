# Decision Log

Record significant technical and governance decisions. One entry per decision.

---

## ADR-000: Template

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by ADR-XXX
- **Context:** What situation forced a decision?
- **Decision:** What was decided?
- **Consequences:** What becomes easier/harder? What risks change?
- **Clean-room note:** Confirm no employer-specific information is contained in or required by this decision.

---

## ADR-001: Use a clean-room public harness with private per-company forks

- **Date:** 2026-07-12
- **Status:** Accepted
- **Context:** The same architecture patterns are needed across multiple regulated-industry engagements without transferring any employer's IP.
- **Decision:** Maintain a generalized public reference (this repo). Each engagement forks privately; nothing flows back except rewritten, generalized patterns.
- **Consequences:** Slight duplication across private repos; strong IP and data boundaries; public repo stays useful as a portfolio and starting point.
- **Clean-room note:** This repo contains only synthetic and generalized content.

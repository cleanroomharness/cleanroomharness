# Clean-Room Policy

This policy defines what may move between companies and what may not. It exists so the same person or team can build AI systems for multiple employers or clients without transferring anyone's intellectual property.

## Allowed reusable assets

- Architecture patterns and service boundaries (model gateway, RAG, policy gate, tool adapters, observability, evaluation).
- This public repository and its generalized code.
- Governance templates: this policy, the risk register, the decision log template.
- Public open-source dependencies and their documentation.
- Synthetic demo data created for this repo.
- General skills and knowledge (patterns, not artifacts).

## Forbidden assets — never move between companies

- Employer source code, in whole or in part.
- Employer prompts, prompt fragments, or prompt engineering artifacts.
- Employer or customer data of any kind, including case, call, and claim data.
- Credentials, API keys, certificates, and tokens.
- Screenshots of internal systems.
- Internal architecture diagrams.
- Logs, traces, eval outputs, or telemetry from employer systems.
- Roadmaps, capture/proposal material, and contract-specific artifacts.
- Anything produced on employer time, unless explicitly approved for release in writing.

## Separation rules

1. **One repo per boundary.** This public repo holds only generalized patterns. Each employer gets its own private repo; content never moves between private repos.
2. **Downstream only.** The public harness may flow into a private repo. Nothing flows from a private repo back to public without being rewritten as a generalized pattern and approved.
3. **No shared workspaces.** Do not open employer repos and this repo in the same working session where copy/paste mistakes are likely; keep separate machines or profiles where required by contract.
4. **Synthetic data only.** All examples, evals, and fixtures in the public repo are invented. If a fixture resembles real data, replace it.
5. **Check before commit.** `make check` runs the clean-room scan; CI runs it on every push.

## Employer-specific repo guidance

- Name private repos clearly (e.g., `<company>-ai-harness`) and keep them in the company's own org and infrastructure where possible.
- Company connectors, prompts, model endpoints, and data classifications live only there.
- Record deviations from this harness in the private repo's decision log.

## No data movement between employers

There are no exceptions. If a piece of information came from Company A, it does not appear in Company B's systems, repos, prompts, tickets, or conversations — including "just as an example."

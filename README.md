# CleanRoom Harness

CleanRoom Harness is a clean-room, company-portable AI systems architecture and implementation harness for regulated enterprise and government workflows.

It gives teams a reusable open-source pattern for AI systems engineering while keeping employer-specific data, prompts, code, credentials, traces, logs, diagrams, and implementation details out of the public repo and out of other companies' environments.

**The architecture is portable. Implementations are not.**

Website: https://CleanRoomHarness.com

## What it is

- A reference architecture: FastAPI + policy gate + LiteLLM model gateway + Postgres/pgvector retrieval + tool adapters + audit trail + OpenTelemetry + eval templates.
- A safe public starting point for private, company-specific deployments.
- A set of governance templates (clean-room policy, risk register, decision log) for teams that work across company boundaries.

## What it is not

- Not a product and not production-hardened security.
- Not a place for any employer's code, data, prompts, or architecture.
- Not a bypass for your employment agreements — get explicit approval before releasing anything produced on employer time.

## ⚠️ Clean-room warning

Nothing employer-specific ever enters this repo. That includes source code, prompts, customer/case/call/claim data, credentials, API keys, screenshots, internal diagrams, logs, traces, eval outputs, roadmaps, and proposal material. See [governance/clean_room_policy.md](governance/clean_room_policy.md). Run `make check` before every commit.

## Architecture

```text
[User / App / Agent / Analyst]
        |
        v
[FastAPI API + Streaming Layer]
        |
        +--> [Policy Gate]                 AuthN/AuthZ, PII/PHI/CUI guardrails,
        |                                  prompt-injection checks, tool approval,
        |                                  data-boundary enforcement
        |
        +--> [LiteLLM Model Gateway]       Ollama local, OpenAI-compatible APIs,
        |                                  Azure OpenAI, Anthropic, Bedrock, Gemini,
        |                                  government-approved endpoints
        |
        +--> [Retrieval Layer]             Postgres + pgvector, optional Qdrant,
        |                                  metadata + source citations
        |
        +--> [Tool / Connector Layer]      MCP-style adapters, dry-run first,
        |                                  human approval before side effects
        |
        +--> [Observability + Evaluation]  OpenTelemetry, audit_events,
                                           eval contracts, regression tests
```

More detail: [architecture/portable_architecture.md](architecture/portable_architecture.md)

## Quickstart

```bash
cp .env.example .env
docker compose up --build
```

Services:

| Service  | URL                     |
|----------|-------------------------|
| API      | http://localhost:8080   |
| LiteLLM  | http://localhost:4000   |
| Postgres | localhost:5432          |
| Qdrant   | http://localhost:6333   |
| Redis    | localhost:6379          |

The default model is `ollama/llama3.2:3b`, served by [Ollama](https://ollama.com) running on the host (`ollama pull llama3.2:3b`). Swap models by editing `infra/litellm/config.yaml` or passing `model` in the request.

### Run without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install pytest ruff
make dev    # API only; retrieval falls back to an in-memory demo store
make test
```

## API examples

```bash
# Health
curl http://localhost:8080/health

# Chat (routes through LiteLLM)
curl -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages": [{"role": "user", "content": "Say hello in one sentence."}]}'

# Ingest synthetic text
curl -X POST http://localhost:8080/ingest \
  -H 'Content-Type: application/json' \
  -d '{"source": "synthetic-handbook", "text": "Demo agencies process permit applications within ten business days."}'

# Retrieve with citations
curl -X POST http://localhost:8080/retrieve \
  -H 'Content-Type: application/json' \
  -d '{"query": "permit applications"}'

# Tool dry run (never executes side effects)
curl -X POST http://localhost:8080/tools/dry-run \
  -H 'Content-Type: application/json' \
  -d '{"tool": "demo_ticket", "arguments": {"title": "Synthetic demo ticket"}}'
```

## Deployment options

| Tier | How | When |
|------|-----|------|
| **Lean** | `docker compose up --build` | Local development, demos |
| **K3s** | `make deploy-k3s` | Single node, edge, air-gapped, small regulated environments |
| **K8s** | `make deploy-k8s` | Multi-node enterprise clusters (EKS/AKS/GKE/on-prem) |

The K3s and K8s paths share one kustomize base; overlays differ only in ingress, replicas, and image source. See [infra/k8s/README.md](infra/k8s/README.md) — including the note on replacing the dev-only secret generator before any real deployment.

**Air-gapped environments:** the stack runs fully disconnected — image tags are pinned, Qdrant/LiteLLM telemetry is disabled, and the API makes no external calls. `make airgap-bundle` builds a checksummed transfer bundle (images + import instructions) on a connected host; see the air-gapped section of [infra/k8s/README.md](infra/k8s/README.md).

## MCP server

The harness tools are also available over the [Model Context Protocol](https://modelcontextprotocol.io) for MCP clients like Claude Code and Claude Desktop:

```bash
make mcp    # stdio server: policy gate + audit + dry-run-first, same as the HTTP API
```

See [connectors/mcp/README.md](connectors/mcp/README.md) for client configuration.

## Environment variables

See [.env.example](.env.example). Highlights:

| Variable | Default | Purpose |
|----------|---------|---------|
| `API_AUTH_KEY` | *(empty)* | Shared API key; empty disables auth for local dev |
| `LITELLM_BASE_URL` | `http://localhost:4000` | Model gateway endpoint |
| `DEFAULT_MODEL` | `ollama/llama3.2:3b` | Default model behind LiteLLM |
| `DATABASE_URL` | local Postgres | Documents + audit events |
| `TOOLS_EXECUTION_ENABLED` | `false` | Side-effecting tool execution stays off by default |
| `OTEL_ENABLED` | `false` | OpenTelemetry instrumentation |

## How to customize per employer

1. Create a **private** fork or a new private repo per company: `gh repo create <company>-ai-harness --private`.
2. Add company-specific connectors under `connectors/` **in the private repo only**, implementing `connectors/interfaces/tool_contract.py`.
3. Point `infra/litellm/config.yaml` at approved model endpoints; keep keys in the deployment's secret manager.
4. Replace policy-gate rules with the company's data-classification and approval requirements.
5. Never merge company-specific changes back into this public repo — improvements flow upstream only as generalized patterns.

## What never belongs in this repo

Employer source code, prompts, data, customer/case/call/claim records, credentials, API keys, screenshots of internal systems, internal architecture diagrams, logs, traces, eval outputs, telemetry, roadmaps, capture/proposal material, contract artifacts, or anything produced on employer time without explicit release approval.

## Checks and tests

```bash
make check   # clean-room sanity scan
make lint    # ruff
make test    # pytest
```

## Contributing

Contributions are welcome if they are generalized and synthetic. By contributing you confirm your changes contain no employer-specific material and that you have the right to release them under Apache-2.0. Every PR must pass `make check`.

## License

[Apache-2.0](LICENSE)

# Portable Architecture

## Logical layers

1. **Client layer** — users, apps, agents, or analysts calling the API.
2. **API + streaming layer** — FastAPI; thin routers, typed request models, streaming-ready.
3. **Policy gate** — runs before model calls, ingestion, retrieval, and tool use. AuthN/AuthZ hooks, PII/PHI/CUI guardrails, prompt-injection checks, tool-use approval, data-boundary enforcement. Every decision is structured (`PolicyDecision`) and auditable.
4. **Model gateway** — a LiteLLM proxy behind `app/llm_gateway.py`. All model traffic uses the OpenAI-compatible shape, so providers (Ollama, Azure OpenAI, Anthropic, Bedrock, Gemini, government-approved endpoints) are a config change.
5. **Retrieval layer** — Postgres with pgvector (Qdrant optional). Documents carry tenant ID, source metadata, and a content hash so answers can cite their grounding.
6. **Tool / connector layer** — MCP-style adapters implementing a single contract: `validate`, `dry_run`, `execute(approved_by=...)`. Dry-run first; execution off by default; company connectors live only in private repos.
7. **Observability + evaluation** — OpenTelemetry traces, an `audit_events` table, eval contracts with forbidden outputs, and regression tests.

## ModelOps flow

```
request -> policy gate -> llm_gateway -> LiteLLM proxy -> provider
        -> audit event (actor, model, decision, latency, trace id)
```

Swapping or adding a model touches `infra/litellm/config.yaml` only. Requests may override the model name; environments pin defaults via `DEFAULT_MODEL`.

## RAG flow

```
ingest: text -> policy gate -> documents table (tenant, source, hash, [embedding])
query:  question -> policy gate -> retrieve (keyword now, vector when enabled)
        -> snippets + citations -> prompt assembly -> model gateway -> answer with sources
```

The schema ships with an `embedding vector(768)` column so moving from keyword to vector search is an implementation change, not a migration.

## Tool-use flow

```
propose -> validate(arguments)          # no external contact
        -> dry_run(arguments)           # describes exactly what would happen
        -> human approval               # approved_by recorded
        -> execute(arguments, approved_by)   # only if TOOLS_EXECUTION_ENABLED
        -> audit event
```

## Government / regulated-enterprise considerations

- **Model endpoints:** restrict the LiteLLM config to approved endpoints (e.g., FedRAMP-authorized regions, on-prem Ollama for air-gapped work).
- **Data boundaries:** tenant IDs on every document and audit event; policy gate is the single choke point for classification checks (PII/PHI/CUI).
- **Auditability:** every model call, ingest, retrieval, and tool action can write an audit event with actor, decision, and reason.
- **Least capability:** tools are deny-by-default; side effects require named human approval.
- **No sensitive telemetry:** traces carry IDs and metadata, never raw payloads or secrets.

## Local vs enterprise deployment

| Concern | Local (this repo) | Enterprise |
|---------|-------------------|------------|
| Models | Ollama via LiteLLM | Approved cloud/gov endpoints via the same gateway |
| Auth | Optional shared key | OIDC/mTLS, RBAC, per-tenant authorization |
| Secrets | `.env` (never committed) | Secret manager / vault |
| Data | Synthetic only | Classified per company policy, private repo |
| Observability | Console exporter | OTLP collector + Langfuse/Phoenix |
| Deployment | Docker Compose | Kubernetes/Helm, IaC, network isolation |

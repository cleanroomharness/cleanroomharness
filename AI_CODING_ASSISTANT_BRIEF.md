# AI Coding Assistant Project Brief: CleanRoom Harness

## Purpose

Build and publish **CleanRoom Harness**, a generalized, clean-room, open-source AI systems architecture that can be reused across companies without transferring proprietary code, data, prompts, credentials, internal diagrams, logs, traces, or employer-specific implementation details.

CleanRoom Harness should be safe to use as a public GitHub reference architecture and as a starting point for private company-specific deployments.

## Project identity

**Name:** CleanRoom Harness

**Domain:** `CleanRoomHarness.com`

**Repo name:** `cleanroom-harness`

**Positioning:** A clean-room, company-portable AI systems harness for regulated enterprise and government workflows.

**One-line description:** CleanRoom Harness is an open-source reference architecture and implementation harness for building AI systems without carrying proprietary data, prompts, code, credentials, logs, traces, or employer-specific implementation details across company boundaries.

**Tagline options:**
- Portable architecture. Protected boundaries.
- Build once. Contaminate never.
- Open patterns. Clean boundaries.
- A clean-room harness for enterprise AI.
- Reusable AI systems without reusable employer IP.
- The safe starting point for company-portable AI.


## Working name

Primary name:

`CleanRoom Harness`

Primary domain:

`CleanRoomHarness.com`

Primary GitHub repo name:

`cleanroom-harness`

Alternative repo names if needed:
- `clean-room-harness`
- `cleanroomharness`
- `cleanroom-ai-harness`
- `portable-ai-cleanroom`

## Core principle

The architecture is portable. Implementations are not.

Reusable across companies:
- Architecture patterns
- Service boundaries
- Model gateway pattern
- RAG pattern
- Tool adapter pattern
- Observability pattern
- Evaluation framework
- Governance templates
- Clean-room policy
- Public open-source dependencies
- Synthetic demo data

Never reuse across companies:
- Employer source code
- Employer prompts
- Employer data
- Customer/case/call/claim data
- Credentials
- API keys
- Screenshots of internal systems
- Internal architecture diagrams
- Logs, traces, eval outputs, or telemetry from employer systems
- Roadmaps
- Capture/proposal material
- Contract-specific artifacts
- Anything produced on employer time unless explicitly approved for release

## Target architecture

```text
[User / App / Agent / Analyst]
        |
        v
[FastAPI API + Streaming Layer]
        |
        +--> [Policy Gate]
        |        +--> AuthN/AuthZ
        |        +--> PII/PHI/CUI guardrails
        |        +--> Prompt-injection checks
        |        +--> Tool-use approval
        |        +--> Data-boundary enforcement
        |
        +--> [LiteLLM Model Gateway]
        |        +--> Local Ollama models
        |        +--> OpenAI-compatible APIs
        |        +--> Azure OpenAI
        |        +--> Anthropic
        |        +--> AWS Bedrock
        |        +--> Gemini
        |        +--> Government-approved model endpoints
        |
        +--> [Retrieval Layer]
        |        +--> Postgres + pgvector
        |        +--> Qdrant optional
        |        +--> Document metadata
        |        +--> Source citations
        |
        +--> [Tool / Connector Layer]
        |        +--> MCP-style adapters
        |        +--> Dry-run first
        |        +--> Human approval before side effects
        |        +--> Company-specific connectors only in private repos
        |
        +--> [Observability + Evaluation]
                 +--> OpenTelemetry
                 +--> Langfuse or Phoenix
                 +--> audit_events table
                 +--> eval contracts
                 +--> regression tests
```

## Recommended open-source stack

### API and orchestration

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic
- httpx

### Model gateway

- LiteLLM proxy
- Ollama-compatible local model path
- OpenAI-compatible request format

### Retrieval and data

- Postgres
- pgvector
- Qdrant as optional dedicated vector DB
- Redis for short-lived state, queues, locks, and session memory

### Governance and safety

- Policy-gate module
- Audit-events table
- Clean-room policy
- Human approval before side-effecting actions
- Configurable data-classification hooks

### Observability

- OpenTelemetry instrumentation
- Langfuse or Phoenix compatibility
- Structured logs
- Trace IDs on model calls and tool calls

### Development and deployment

- Docker Compose for local development
- `.env.example`
- Makefile
- GitHub Actions CI
- Ruff or equivalent linting
- Pytest
- Pre-commit hooks optional

## Desired repository structure

```text
cleanroom-harness/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
├── pyproject.toml
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── settings.py
│   ├── llm_gateway.py
│   ├── security.py
│   ├── telemetry.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── chat.py
│   │   ├── ingest.py
│   │   ├── retrieve.py
│   │   └── tools.py
│   └── services/
│       ├── __init__.py
│       ├── retrieval_service.py
│       ├── policy_service.py
│       ├── audit_service.py
│       └── evaluation_service.py
├── connectors/
│   ├── README.md
│   └── interfaces/
│       ├── __init__.py
│       └── tool_contract.py
├── policies/
│   ├── README.md
│   ├── clean_room_policy.md
│   └── data_boundary_policy.md
├── prompts/
│   ├── README.md
│   └── system_portable.md
├── evals/
│   ├── README.md
│   ├── eval_contract.md
│   └── synthetic_cases.jsonl
├── governance/
│   ├── clean_room_policy.md
│   ├── risk_register.md
│   └── decision_log_template.md
├── architecture/
│   ├── portable_architecture.md
│   └── diagrams/
│       └── logical_architecture.mmd
├── infra/
│   ├── postgres/
│   │   └── init.sql
│   └── litellm/
│       └── config.yaml
├── scripts/
│   ├── bootstrap.sh
│   └── check_clean_room.sh
└── tests/
    ├── test_health.py
    ├── test_policy.py
    └── test_tool_dry_run.py
```

## Functional requirements

### 1. Local startup

The repo must run locally with:

```bash
cp .env.example .env
docker compose up --build
```

Minimum local services:
- API on `localhost:8080`
- LiteLLM proxy on `localhost:4000`
- Postgres on `localhost:5432`
- Qdrant on `localhost:6333`
- Redis on `localhost:6379`

### 2. API endpoints

Implement these starter endpoints:

```text
GET  /health
POST /chat
POST /ingest
POST /retrieve
POST /tools/dry-run
```

Expected behavior:
- `/health` returns simple service status.
- `/chat` calls the model gateway through LiteLLM.
- `/ingest` accepts demo text only and stores metadata safely.
- `/retrieve` performs placeholder retrieval or simple mock retrieval if full vectorization is not yet implemented.
- `/tools/dry-run` validates tool requests without executing side effects.

### 3. Model gateway

All model calls must go through `app/llm_gateway.py`.

Do not call model providers directly from routers.

Use an OpenAI-compatible request shape so models can be swapped behind LiteLLM.

Default local model name:

```text
ollama/llama3.2:3b
```

The code should allow users to override this through request payloads or environment config.

### 4. Policy gate

Create a policy gate that runs before:
- model calls
- ingestion
- retrieval
- tool calls
- side-effecting actions

Initial checks can be simple string-based guardrails, but the interface should support future expansion.

The policy gate should block obvious requests such as:
- exporting customer data
- reusing proprietary prompts
- copying employer code
- pasting confidential data
- using credentials
- executing side-effecting tools without approval

### 5. Tool adapter pattern

Create a neutral tool adapter interface.

The interface should support:
- `validate(arguments)`
- `dry_run(arguments)`
- `execute(arguments, approved_by=None)`

Rules:
- Public repo may include only neutral example tools.
- Company-specific connectors must not be included in the public repo.
- Tool execution should be disabled by default.
- Side-effecting tools require human approval.

### 6. Retrieval

Implement a simple retrieval pattern using:
- document table in Postgres
- optional pgvector column when embeddings are added
- source metadata
- tenant ID
- content hash
- created timestamp

Initial version may store text without embeddings, but the structure should be ready for vector search.

### 7. Audit events

Create an `audit_events` table for:
- actor
- action
- resource type
- resource ID
- tenant ID
- policy decision
- reason
- timestamp

Every model call, ingest event, retrieval event, and tool dry run should be able to create an audit entry.

### 8. Observability

Add OpenTelemetry instrumentation for FastAPI.

The repo should be structured so future traces can capture:
- request ID
- user/actor ID where available
- tenant ID
- model name
- tool name
- policy decision
- latency
- error state

Do not log raw secrets or sensitive payloads.

### 9. Evaluation framework

Create a basic eval contract that defines:
- task name
- inputs
- expected outputs
- forbidden outputs
- grounding source
- scoring method
- human review threshold
- failure examples
- rollback plan
- operational metric

Add synthetic examples only.

No employer data.

### 10. Clean-room checks

Add a script:

```bash
make check
```

It should look for obvious forbidden file names or secret-like artifacts, such as:
- `.pem`
- `.key`
- `secret`
- `token`
- `credential`
- `password`

This is not sufficient for real security, but it is a useful pre-commit sanity check.

## Documentation requirements

Create or update these docs.

### README.md

Must include:
- What the project is
- What it is not
- Clean-room warning
- Architecture diagram
- Quickstart
- Environment variables
- How to customize per employer
- What never belongs in this repo
- How to create a private company-specific fork
- Basic API examples
- Contributing note

### governance/clean_room_policy.md

Must clearly define:
- allowed reusable assets
- forbidden assets
- separation rules
- employer-specific repo guidance
- no data movement between employers

### governance/risk_register.md

Include at least these risks:
- data leakage
- prompt leakage
- tool overreach
- hallucinated actions
- PII/PHI/CUI mishandling
- timekeeping conflict
- organizational conflict of interest
- unclear IP ownership

### architecture/portable_architecture.md

Must explain:
- logical layers
- ModelOps flow
- RAG flow
- tool-use flow
- government/regulated-enterprise considerations
- local vs enterprise deployment differences

### prompts/system_portable.md

Starter system prompt should say:
- Do not request proprietary data unless authorized.
- Do not expose secrets.
- Ask for approval before side effects.
- Use citations when retrieval is available.
- Treat company-specific connectors as unavailable unless enabled.
- Prefer auditable steps.

## GitHub setup tasks

Initialize git:

```bash
git init
git add .
git commit -m "Initial clean-room portable AI architecture"
```

Create GitHub repo:

```bash
gh repo create cleanroom-harness --public --source=. --remote=origin --push
```

If using a private repo first:

```bash
gh repo create cleanroom-harness --private --source=. --remote=origin --push
```

Recommended first branches:
- `main`
- `dev`
- `feature/model-gateway`
- `feature/retrieval`
- `feature/policy-gate`
- `feature/evals`
- `feature/observability`

## Suggested README opening

```markdown
# CleanRoom Harness

CleanRoom Harness is a clean-room, company-portable AI systems architecture and implementation harness for regulated enterprise and government workflows.

It gives teams a reusable open-source pattern for AI systems engineering while keeping employer-specific data, prompts, code, credentials, traces, logs, diagrams, and implementation details out of the public repo and out of other companies’ environments.

The architecture is portable. Implementations are not.

Website: https://CleanRoomHarness.com
```


## Suggested GitHub description

CleanRoom Harness: a clean-room, company-portable open-source AI systems harness for regulated enterprise and government workflows.

## Suggested GitHub homepage

```text
https://CleanRoomHarness.com
```

## Suggested GitHub topics

```text
ai
agents
rag
fastapi
litellm
pgvector
qdrant
opentelemetry
modelops
llmops
governance
responsible-ai
clean-room
government-ai
enterprise-ai
```

## Suggested LICENSE

Use either:
- Apache-2.0 if patent protection and enterprise reuse matter.
- MIT if maximum simplicity matters.

Recommended: `Apache-2.0`.

## Landing page direction for CleanRoomHarness.com

Use the domain as the public face of the project.

Suggested hero copy:

```text
CleanRoom Harness
Portable AI architecture. Protected company boundaries.

An open-source reference architecture for building AI systems across regulated enterprise and government environments without carrying proprietary code, data, prompts, credentials, traces, or implementation details between companies.
```

Suggested primary call to action:

```text
View on GitHub
```

Suggested secondary call to action:

```text
Read the Clean-Room Policy
```

Suggested sections:
- What it is
- What it is not
- Architecture
- Clean-room rules
- Quickstart
- Government and regulated-enterprise use cases
- Roadmap
- Contributing

## Coding style

- Keep code simple and explicit.
- Prefer readable modules over clever abstractions.
- Keep routers thin.
- Put logic in services.
- Keep model-provider logic isolated in the model gateway.
- Keep policy decisions structured and auditable.
- Use type hints.
- Add tests for every policy behavior.
- Never hardcode secrets.
- Never include company-specific examples.

## Acceptance criteria

The repo is ready when:

- `docker compose up --build` starts all services.
- `GET /health` returns status OK.
- `POST /chat` routes through LiteLLM.
- `POST /tools/dry-run` never executes side effects.
- `.env.example` exists and contains no real secrets.
- README explains clean-room constraints.
- Governance docs are present.
- Risk register is present.
- Architecture docs are present.
- `make check` runs.
- Tests run locally.
- No employer-specific artifacts are present.
- No secrets are present.
- Initial GitHub commit is clean and generalized.

## Important boundary note for AI coding assistants

Do not infer or add details from any current or past employer.

Do not include names, systems, internal workflows, screenshots, prompts, customer data, call data, claim data, case data, proposal material, capture strategy, or private architecture from any employer.

This repository should remain a generalized, synthetic, open-source reference architecture only.

## First implementation plan

1. Confirm repo structure.
2. Add missing `.gitignore`, `LICENSE`, `pyproject.toml`, and tests.
3. Ensure all files are generalized.
4. Build local Docker stack.
5. Fix startup errors.
6. Add basic CI.
7. Run clean-room check.
8. Commit initial version.
9. Push to GitHub.
10. Open issues for future enhancements.

## Future enhancements

Create GitHub issues for:

- Add pgvector embeddings pipeline
- Add local embedding model support
- Add retrieval citations
- Add Langfuse integration
- Add Phoenix integration
- Add OpenTelemetry collector
- Add MCP server example
- Add human-approval workflow
- Add role-based access control
- Add multi-tenant isolation
- Add synthetic government-service demo
- Add synthetic contact-center agent-assist demo
- Add synthetic document-intake demo
- Add CI security scanning
- Add SBOM generation
- Add Helm chart
- Add Terraform examples
- Add Azure deployment guide
- Add AWS deployment guide
- Add air-gapped deployment guide
- Add FedRAMP/RMF control mapping placeholder

## Prompt to continue work

Use this instruction with Codex, Claude Code, or another AI coding assistant:

```text
You are helping build a public GitHub repository called cleanroom-harness for CleanRoom Harness.

Follow the project brief in AI_CODING_ASSISTANT_BRIEF.md exactly.

Your job is to improve the repo into a clean-room, company-portable, open-source AI systems architecture using FastAPI, LiteLLM, Postgres/pgvector, Qdrant, Redis, policy gates, tool adapters, OpenTelemetry, and evaluation templates.

Do not add employer-specific code, data, prompts, architecture, diagrams, screenshots, logs, traces, credentials, or examples.

Keep the implementation generalized and synthetic.

Before making changes:
1. Inspect the repository.
2. Identify gaps against the acceptance criteria.
3. Propose a short implementation plan.
4. Make the smallest useful set of changes.
5. Run tests and checks if available.
6. Summarize what changed and what remains.
```

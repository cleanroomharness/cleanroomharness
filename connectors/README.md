# Connectors

Tool adapters follow the contract in
[interfaces/tool_contract.py](interfaces/tool_contract.py):
`validate(arguments)` → `dry_run(arguments)` → `execute(arguments, approved_by=...)`.

Rules:

- **This public repo contains neutral example tools only** ([examples/](examples/)).
- Company-specific connectors (ticketing, CRM, case systems, internal APIs) are implemented in **private repos only** and never merged here.
- Dry-run must be side-effect free and describe exactly what execute would do.
- Tool execution is disabled by default (`TOOLS_EXECUTION_ENABLED=false`); side-effecting tools additionally require a named human approver.
- Every tool call should produce an audit event.

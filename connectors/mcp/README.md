# MCP Server

An example [Model Context Protocol](https://modelcontextprotocol.io) server
that exposes the harness's neutral example tools to MCP clients (Claude Code,
Claude Desktop, or any other MCP-capable agent) over stdio.

It reuses the same services as the HTTP API, so the guarantees are identical:
policy gate first, audit event on every call, dry-run by default, execution
disabled unless `TOOLS_EXECUTION_ENABLED=true` plus a named human approver.

## Exposed MCP tools

| MCP tool | What it does |
|----------|--------------|
| `list_harness_tools` | Lists registered harness tools with side-effect flags |
| `dry_run_tool` | Validates + dry-runs a harness tool; never causes side effects |
| `execute_tool` | Executes a tool — refuses unless execution is enabled and approved |
| `retrieve_documents` | Keyword retrieval over stored demo documents, with citations |

## Run

```bash
make mcp
# or
python -m connectors.mcp.server
```

## Client configuration

Claude Code (`.mcp.json` in your project):

```json
{
  "mcpServers": {
    "cleanroom-harness": {
      "command": "python",
      "args": ["-m", "connectors.mcp.server"],
      "cwd": "/path/to/cleanroomharness"
    }
  }
}
```

## Clean-room note

The public server registers neutral example tools only. Company-specific
connectors register their tools in `app/services/tool_registry.py` in a
**private fork** — never here.

"""MCP server example.

Exposes the harness's neutral example tools over the Model Context Protocol
(stdio transport), so MCP clients (Claude Code, Claude Desktop, other agents)
can use them. Every call carries the same guarantees as the HTTP API:

- the policy gate runs before anything else,
- every call writes an audit event,
- dry-run is the default interaction,
- execution is disabled unless TOOLS_EXECUTION_ENABLED=true AND a named
  human approver is supplied.

Run:  python -m connectors.mcp.server
"""

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.services import audit_service, retrieval_service
from app.services.policy_service import PolicyAction, evaluate
from app.services.tool_registry import get_registry
from app.settings import get_settings

mcp = FastMCP("cleanroom-harness")


@mcp.tool()
def list_harness_tools() -> list[dict[str, Any]]:
    """List the harness tools available through this MCP server."""
    return [
        {"name": tool.name, "description": tool.description, "side_effects": tool.side_effects}
        for tool in get_registry().values()
    ]


@mcp.tool()
def dry_run_tool(
    tool: str,
    arguments: dict[str, Any],
    actor: str = "mcp-client",
    tenant_id: str = "demo",
) -> dict[str, Any]:
    """Validate and dry-run a harness tool. Never causes side effects."""
    adapter = get_registry().get(tool)
    if adapter is None:
        return {"executed": False, "error": f"unknown tool '{tool}'"}

    decision = evaluate(PolicyAction.TOOL_DRY_RUN, json.dumps(arguments))
    audit_service.record(
        actor=actor,
        action="mcp_tool_dry_run",
        resource_type="tool",
        resource_id=adapter.name,
        tenant_id=tenant_id,
        policy_decision="allow" if decision.allowed else "deny",
        reason=decision.reason,
    )
    if not decision.allowed:
        return {"executed": False, "allowed": False, "detail": decision.reason}

    validation = adapter.validate(arguments)
    if not validation.ok:
        return {"executed": False, "allowed": True, "valid": False, "detail": validation.message}

    result = adapter.dry_run(arguments)
    return {
        "executed": False,
        "allowed": True,
        "valid": True,
        "side_effects": adapter.side_effects,
        "dry_run": {"ok": result.ok, "message": result.message, "output": result.output},
    }


@mcp.tool()
def execute_tool(
    tool: str,
    arguments: dict[str, Any],
    approved_by: str | None = None,
    actor: str = "mcp-client",
    tenant_id: str = "demo",
) -> dict[str, Any]:
    """Execute a harness tool.

    Disabled unless TOOLS_EXECUTION_ENABLED=true; side-effecting tools also
    require a named human approver in approved_by.
    """
    settings = get_settings()
    adapter = get_registry().get(tool)
    if adapter is None:
        return {"executed": False, "error": f"unknown tool '{tool}'"}

    if not settings.tools_execution_enabled:
        audit_service.record(
            actor=actor,
            action="mcp_tool_execute",
            resource_type="tool",
            resource_id=adapter.name,
            tenant_id=tenant_id,
            policy_decision="deny",
            reason="tool execution disabled (TOOLS_EXECUTION_ENABLED=false)",
        )
        return {
            "executed": False,
            "allowed": False,
            "detail": "tool execution is disabled by default; set TOOLS_EXECUTION_ENABLED=true",
        }

    action = PolicyAction.TOOL_EXECUTE if adapter.side_effects else PolicyAction.TOOL_DRY_RUN
    decision = evaluate(action, json.dumps(arguments), context={"approved_by": approved_by})
    audit_service.record(
        actor=actor,
        action="mcp_tool_execute",
        resource_type="tool",
        resource_id=adapter.name,
        tenant_id=tenant_id,
        policy_decision="allow" if decision.allowed else "deny",
        reason=decision.reason,
    )
    if not decision.allowed:
        return {"executed": False, "allowed": False, "detail": decision.reason}

    result = adapter.execute(arguments, approved_by=approved_by)
    return {"executed": result.ok, "message": result.message, "output": result.output}


@mcp.tool()
def retrieve_documents(
    query: str,
    tenant_id: str = "demo",
    top_k: int = 5,
    actor: str = "mcp-client",
) -> dict[str, Any]:
    """Retrieve stored demo documents with source citations."""
    decision = evaluate(PolicyAction.RETRIEVE, query)
    audit_service.record(
        actor=actor,
        action="mcp_retrieve",
        resource_type="documents",
        tenant_id=tenant_id,
        policy_decision="allow" if decision.allowed else "deny",
        reason=decision.reason,
    )
    if not decision.allowed:
        return {"allowed": False, "detail": decision.reason, "results": []}

    results = retrieval_service.retrieve(tenant_id=tenant_id, query=query, top_k=top_k)
    return {"allowed": True, "query": query, "results": results, "count": len(results)}


if __name__ == "__main__":
    mcp.run()

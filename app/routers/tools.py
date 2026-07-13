import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.security import require_api_key
from app.services import audit_service
from app.services.policy_service import PolicyAction, evaluate
from app.settings import get_settings
from connectors.examples.demo_ticket_tool import DemoTicketTool
from connectors.examples.echo_tool import EchoTool
from connectors.interfaces.tool_contract import ToolContract

router = APIRouter(prefix="/tools", tags=["tools"], dependencies=[Depends(require_api_key)])

# Public registry holds neutral example tools only. Company-specific
# connectors register their own tools in private forks.
_REGISTRY: dict[str, ToolContract] = {
    tool.name: tool for tool in (EchoTool(), DemoTicketTool())
}


class ToolRequest(BaseModel):
    tool: str = Field(min_length=1)
    arguments: dict = Field(default_factory=dict)
    tenant_id: str = "demo"
    actor: str = "anonymous"
    approved_by: str | None = None


def _get_tool(name: str) -> ToolContract:
    tool = _REGISTRY.get(name)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"unknown tool '{name}'")
    return tool


@router.get("")
async def list_tools() -> dict:
    return {
        "tools": [
            {"name": tool.name, "description": tool.description, "side_effects": tool.side_effects}
            for tool in _REGISTRY.values()
        ]
    }


@router.post("/dry-run")
async def dry_run(request: ToolRequest) -> dict:
    tool = _get_tool(request.tool)
    decision = evaluate(PolicyAction.TOOL_DRY_RUN, json.dumps(request.arguments))
    audit_service.record(
        actor=request.actor,
        action="tool_dry_run",
        resource_type="tool",
        resource_id=tool.name,
        tenant_id=request.tenant_id,
        policy_decision="allow" if decision.allowed else "deny",
        reason=decision.reason,
    )
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)

    validation = tool.validate(request.arguments)
    if not validation.ok:
        return {"executed": False, "valid": False, "detail": validation.message}

    result = tool.dry_run(request.arguments)
    return {
        "executed": False,
        "valid": True,
        "side_effects": tool.side_effects,
        "dry_run": {"ok": result.ok, "message": result.message, "output": result.output},
    }


@router.post("/execute")
async def execute(request: ToolRequest) -> dict:
    settings = get_settings()
    tool = _get_tool(request.tool)

    if not settings.tools_execution_enabled:
        audit_service.record(
            actor=request.actor,
            action="tool_execute",
            resource_type="tool",
            resource_id=tool.name,
            tenant_id=request.tenant_id,
            policy_decision="deny",
            reason="tool execution disabled (TOOLS_EXECUTION_ENABLED=false)",
        )
        raise HTTPException(
            status_code=403,
            detail="tool execution is disabled by default; set TOOLS_EXECUTION_ENABLED=true",
        )

    action = PolicyAction.TOOL_EXECUTE if tool.side_effects else PolicyAction.TOOL_DRY_RUN
    decision = evaluate(
        action, json.dumps(request.arguments), context={"approved_by": request.approved_by}
    )
    audit_service.record(
        actor=request.actor,
        action="tool_execute",
        resource_type="tool",
        resource_id=tool.name,
        tenant_id=request.tenant_id,
        policy_decision="allow" if decision.allowed else "deny",
        reason=decision.reason,
    )
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)

    result = tool.execute(request.arguments, approved_by=request.approved_by)
    return {
        "executed": result.ok,
        "message": result.message,
        "output": result.output,
    }

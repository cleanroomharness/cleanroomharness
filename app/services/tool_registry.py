"""Tool registry.

Single source of truth for the tools available to the HTTP API and the MCP
server. The public repo registers neutral example tools only; private forks
register company-specific connectors here.
"""

from connectors.examples.demo_ticket_tool import DemoTicketTool
from connectors.examples.echo_tool import EchoTool
from connectors.interfaces.tool_contract import ToolContract

_REGISTRY: dict[str, ToolContract] = {
    tool.name: tool for tool in (EchoTool(), DemoTicketTool())
}


def get_registry() -> dict[str, ToolContract]:
    return _REGISTRY

"""Neutral example of a side-effecting tool.

Simulates creating a ticket in a fictional tracker. It demonstrates the
approval flow: dry_run describes the action, execute refuses without an
approver. Nothing here talks to any real system.
"""

import uuid
from typing import Any

from connectors.interfaces.tool_contract import ToolContract, ToolResult


class DemoTicketTool(ToolContract):
    name = "demo_ticket"
    description = "Simulates creating a ticket in a fictional tracker. Side-effecting."
    side_effects = True

    def validate(self, arguments: dict[str, Any]) -> ToolResult:
        title = arguments.get("title")
        if not isinstance(title, str) or not title.strip():
            return ToolResult(ok=False, message="'title' must be a non-empty string")
        return ToolResult(ok=True, message="arguments valid")

    def dry_run(self, arguments: dict[str, Any]) -> ToolResult:
        check = self.validate(arguments)
        if not check.ok:
            return check
        return ToolResult(
            ok=True,
            message="dry run: would create a ticket in the fictional tracker",
            output={
                "would_create": {
                    "title": arguments["title"],
                    "body": arguments.get("body", ""),
                },
                "requires_approval": True,
            },
        )

    def execute(self, arguments: dict[str, Any], approved_by: str | None = None) -> ToolResult:
        check = self.validate(arguments)
        if not check.ok:
            return check
        if not approved_by:
            return ToolResult(
                ok=False, message="side-effecting tool requires human approval (approved_by)"
            )
        return ToolResult(
            ok=True,
            message="simulated ticket created",
            output={"ticket_id": f"DEMO-{uuid.uuid4().hex[:8]}", "approved_by": approved_by},
        )

"""Neutral example tool with no side effects."""

from typing import Any

from connectors.interfaces.tool_contract import ToolContract, ToolResult


class EchoTool(ToolContract):
    name = "echo"
    description = "Returns the provided message. No side effects; demo only."
    side_effects = False

    def validate(self, arguments: dict[str, Any]) -> ToolResult:
        message = arguments.get("message")
        if not isinstance(message, str) or not message.strip():
            return ToolResult(ok=False, message="'message' must be a non-empty string")
        return ToolResult(ok=True, message="arguments valid")

    def dry_run(self, arguments: dict[str, Any]) -> ToolResult:
        check = self.validate(arguments)
        if not check.ok:
            return check
        return ToolResult(
            ok=True,
            message="dry run: would echo the message back",
            output={"would_return": arguments["message"]},
        )

    def execute(self, arguments: dict[str, Any], approved_by: str | None = None) -> ToolResult:
        check = self.validate(arguments)
        if not check.ok:
            return check
        return ToolResult(ok=True, message="echoed", output={"message": arguments["message"]})

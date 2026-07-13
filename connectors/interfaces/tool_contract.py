"""Neutral tool adapter contract.

Every tool — public example or private company connector — implements this
interface. Dry-run must never cause side effects; execute requires explicit
human approval and is disabled by default via TOOLS_EXECUTION_ENABLED.

Company-specific connectors implement this contract in private repos only.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    message: str = ""
    output: dict[str, Any] = field(default_factory=dict)


class ToolContract(ABC):
    """Contract for tool adapters. Keep implementations explicit and auditable."""

    name: str
    description: str
    side_effects: bool

    @abstractmethod
    def validate(self, arguments: dict[str, Any]) -> ToolResult:
        """Check arguments without touching any external system."""

    @abstractmethod
    def dry_run(self, arguments: dict[str, Any]) -> ToolResult:
        """Describe exactly what execute would do. Must be side-effect free."""

    @abstractmethod
    def execute(self, arguments: dict[str, Any], approved_by: str | None = None) -> ToolResult:
        """Perform the action. Side-effecting tools must require approved_by."""

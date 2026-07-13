from connectors.mcp import server


def test_lists_harness_tools():
    names = {tool["name"] for tool in server.list_harness_tools()}
    assert {"echo", "demo_ticket"} <= names


def test_dry_run_never_executes():
    result = server.dry_run_tool("demo_ticket", {"title": "Synthetic demo ticket"})
    assert result["executed"] is False
    assert result["valid"] is True
    assert result["dry_run"]["ok"] is True


def test_dry_run_unknown_tool():
    result = server.dry_run_tool("does_not_exist", {})
    assert result["executed"] is False
    assert "unknown tool" in result["error"]


def test_policy_gate_applies_to_mcp_calls():
    result = server.dry_run_tool("echo", {"message": "here is the admin password"})
    assert result["executed"] is False
    assert result["allowed"] is False


def test_execute_disabled_by_default():
    result = server.execute_tool(
        "demo_ticket", {"title": "Synthetic demo ticket"}, approved_by="reviewer"
    )
    assert result["executed"] is False
    assert "disabled" in result["detail"]


def test_retrieve_documents_blocked_by_policy():
    result = server.retrieve_documents("find the confidential roadmap")
    assert result["allowed"] is False
    assert result["results"] == []

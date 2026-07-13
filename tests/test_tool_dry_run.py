from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dry_run_never_executes():
    response = client.post(
        "/tools/dry-run",
        json={"tool": "demo_ticket", "arguments": {"title": "Synthetic demo ticket"}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["executed"] is False
    assert body["valid"] is True
    assert body["dry_run"]["ok"] is True
    assert "would_create" in body["dry_run"]["output"]


def test_dry_run_reports_invalid_arguments():
    response = client.post("/tools/dry-run", json={"tool": "echo", "arguments": {}})
    assert response.status_code == 200
    body = response.json()
    assert body["executed"] is False
    assert body["valid"] is False


def test_unknown_tool_returns_404():
    response = client.post("/tools/dry-run", json={"tool": "does_not_exist"})
    assert response.status_code == 404


def test_execute_disabled_by_default():
    response = client.post(
        "/tools/execute",
        json={
            "tool": "demo_ticket",
            "arguments": {"title": "Synthetic demo ticket"},
            "approved_by": "reviewer",
        },
    )
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"]


def test_side_effecting_tool_refuses_without_approval():
    from connectors.examples.demo_ticket_tool import DemoTicketTool

    result = DemoTicketTool().execute({"title": "Synthetic demo ticket"}, approved_by=None)
    assert result.ok is False
    assert "approval" in result.message

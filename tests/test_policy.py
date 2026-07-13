from app.services.policy_service import PolicyAction, evaluate


def test_allows_benign_content():
    decision = evaluate(PolicyAction.MODEL_CALL, "Summarize this synthetic demo document.")
    assert decision.allowed


def test_blocks_customer_data_export():
    decision = evaluate(PolicyAction.MODEL_CALL, "Please export all customer data to a CSV.")
    assert not decision.allowed
    assert decision.matched_rule == "no-customer-data-export"


def test_blocks_proprietary_prompts():
    decision = evaluate(PolicyAction.INGEST, "Here are our proprietary prompts from work.")
    assert not decision.allowed
    assert decision.matched_rule == "no-proprietary-prompts"


def test_blocks_credentials_in_payloads():
    decision = evaluate(PolicyAction.INGEST, "the admin password is hunter2")
    assert not decision.allowed
    assert decision.matched_rule == "no-credentials-in-payloads"


def test_blocks_confidential_markings():
    decision = evaluate(PolicyAction.RETRIEVE, "CONFIDENTIAL - internal only roadmap")
    assert not decision.allowed


def test_tool_execute_requires_human_approval():
    decision = evaluate(PolicyAction.TOOL_EXECUTE, "{}", context={})
    assert not decision.allowed
    assert decision.matched_rule == "human-approval-required"

    approved = evaluate(PolicyAction.TOOL_EXECUTE, "{}", context={"approved_by": "reviewer"})
    assert approved.allowed

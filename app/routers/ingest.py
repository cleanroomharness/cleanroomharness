from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.security import require_api_key
from app.services import audit_service, retrieval_service
from app.services.policy_service import PolicyAction, evaluate

router = APIRouter(tags=["ingest"], dependencies=[Depends(require_api_key)])


class IngestRequest(BaseModel):
    tenant_id: str = "demo"
    actor: str = "anonymous"
    source: str = Field(min_length=1, description="Where this demo text came from")
    text: str = Field(min_length=1, description="Demo/synthetic text only")


@router.post("/ingest")
async def ingest(request: IngestRequest) -> dict:
    decision = evaluate(PolicyAction.INGEST, f"{request.source}\n{request.text}")
    if not decision.allowed:
        audit_service.record(
            actor=request.actor,
            action="ingest",
            resource_type="document",
            tenant_id=request.tenant_id,
            policy_decision="deny",
            reason=decision.reason,
        )
        raise HTTPException(status_code=403, detail=decision.reason)

    document = retrieval_service.ingest_text(
        tenant_id=request.tenant_id, source=request.source, text=request.text
    )
    audit_service.record(
        actor=request.actor,
        action="ingest",
        resource_type="document",
        resource_id=document["id"],
        tenant_id=request.tenant_id,
        policy_decision="allow",
        reason=decision.reason,
    )
    return {"stored": True, "document": document}

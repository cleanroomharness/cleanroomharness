from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.security import require_api_key
from app.services import audit_service, retrieval_service
from app.services.policy_service import PolicyAction, evaluate

router = APIRouter(tags=["retrieve"], dependencies=[Depends(require_api_key)])


class RetrieveRequest(BaseModel):
    tenant_id: str = "demo"
    actor: str = "anonymous"
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


@router.post("/retrieve")
async def retrieve(request: RetrieveRequest) -> dict:
    decision = evaluate(PolicyAction.RETRIEVE, request.query)
    audit_service.record(
        actor=request.actor,
        action="retrieve",
        resource_type="documents",
        tenant_id=request.tenant_id,
        policy_decision="allow" if decision.allowed else "deny",
        reason=decision.reason,
    )
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)

    results = retrieval_service.retrieve(
        tenant_id=request.tenant_id, query=request.query, top_k=request.top_k
    )
    return {"query": request.query, "results": results, "count": len(results)}

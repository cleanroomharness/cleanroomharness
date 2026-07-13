from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.llm_gateway import GatewayError, chat_completion
from app.security import require_api_key
from app.services import audit_service
from app.services.policy_service import PolicyAction, evaluate

router = APIRouter(tags=["chat"], dependencies=[Depends(require_api_key)])


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int = 1024
    tenant_id: str = "demo"
    actor: str = "anonymous"


@router.post("/chat")
async def chat(request: ChatRequest) -> dict:
    content = "\n".join(message.content for message in request.messages)
    decision = evaluate(PolicyAction.MODEL_CALL, content)
    audit_service.record(
        actor=request.actor,
        action="chat",
        resource_type="model",
        resource_id=request.model,
        tenant_id=request.tenant_id,
        policy_decision="allow" if decision.allowed else "deny",
        reason=decision.reason,
    )
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)

    try:
        result = await chat_completion(
            messages=[message.model_dump() for message in request.messages],
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except GatewayError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "model": result.get("model"),
        "response": result["choices"][0]["message"]["content"],
        "usage": result.get("usage"),
    }

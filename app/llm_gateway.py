"""Model gateway.

Every model call in the harness goes through this module, which talks to a
LiteLLM proxy using the OpenAI-compatible chat-completions shape. Routers must
never call model providers directly; swapping providers is a LiteLLM config
change, not a code change.
"""

from typing import Any

import httpx

from app.settings import get_settings


class GatewayError(RuntimeError):
    """Raised when the model gateway is unreachable or returns an error."""


async def chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    settings = get_settings()
    payload = {
        "model": model or settings.default_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {settings.litellm_api_key}"}
    url = f"{settings.litellm_base_url}/v1/chat/completions"

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise GatewayError(f"model gateway unreachable: {exc}") from exc

    if response.status_code >= 400:
        raise GatewayError(
            f"model gateway returned {response.status_code}: {response.text[:500]}"
        )
    return response.json()

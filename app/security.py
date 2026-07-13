"""API authentication.

If API_AUTH_KEY is set, every non-health endpoint requires the same value in
the X-API-Key header. An empty API_AUTH_KEY disables auth for local
development. Replace with real AuthN/AuthZ (OIDC, mTLS, etc.) per deployment.
"""

from fastapi import Header, HTTPException

from app.settings import get_settings


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not settings.api_auth_key:
        return
    if x_api_key != settings.api_auth_key:
        raise HTTPException(status_code=401, detail="invalid or missing API key")

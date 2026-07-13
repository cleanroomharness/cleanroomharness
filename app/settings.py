"""Application settings.

All configuration comes from environment variables (or a local .env file).
Defaults are safe for local development and contain no real credentials.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "cleanroom-harness"
    app_version: str = "0.1.0"
    environment: str = "local"
    api_port: int = 8080

    # Optional shared key for API access. Empty string disables auth (local dev).
    api_auth_key: str = ""

    # Model gateway (LiteLLM proxy, OpenAI-compatible).
    litellm_base_url: str = "http://localhost:4000"
    litellm_api_key: str = "local-dev-only"
    default_model: str = "ollama/llama3.2:3b"

    # Data services.
    database_url: str = "postgresql://cleanroom:cleanroom@localhost:5432/cleanroom"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"

    # Side-effecting tool execution is disabled by default.
    tools_execution_enabled: bool = False

    # Observability.
    otel_enabled: bool = False
    otel_exporter_otlp_endpoint: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()

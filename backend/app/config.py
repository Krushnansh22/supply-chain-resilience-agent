"""
app/config.py
Owner: Developer 2 (Backend / Simulation)

Centralized settings object. Every other module should import `settings` from here
instead of calling os.getenv() directly, so the whole team has one place to look.

RECEIVES: values from backend/.env (see .env.example for the full list)
DELIVERS: a singleton `settings` instance used by database.py, agent/, decision_engine/, etc.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database ---
    DATABASE_URL: str = "sqlite:///./data/scda.db"

    # --- LLM ---
    LLM_PROVIDER: str = "anthropic"  # anthropic | openai | gemini
    LLM_MODEL: str = "claude-sonnet-4-6"
    LLM_API_KEY: str = ""

    # --- Business rules (REQUIRED by official PS: >$50,000 impact => human approval) ---
    AUTONOMOUS_APPROVAL_LIMIT_USD: float = 50000.0

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173"
    CORS_ALLOWED_METHODS: str = "GET,POST,OPTIONS"

    # --- Security ---
    # Optional API key for protecting mutating endpoints.
    # If empty (default), all endpoints are open (safe for local dev & hackathon demos).
    # Set API_KEY=your-secret in .env to enforce authentication.
    API_KEY: str = ""

    # Controls whether interactive Swagger UI /docs and openapi.json are publicly accessible
    DOCS_ENABLED: bool = True

    # --- Rate Limiting & Proxy Configuration ---
    # Comma-separated list of trusted reverse proxy IPs (e.g. "127.0.0.1,10.0.0.1").
    # Empty by default (X-Forwarded-For is IGNORED unless direct peer IP is in this list).
    TRUSTED_PROXY_IPS: str = ""
    GENERAL_RATE_LIMIT_MAX: int = 60
    GENERAL_RATE_LIMIT_WINDOW: int = 60

    # --- Misc ---
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def cors_allowed_methods_list(self) -> list[str]:
        return [m.strip().upper() for m in self.CORS_ALLOWED_METHODS.split(",") if m.strip()]

    @property
    def trusted_proxy_ip_list(self) -> list[str]:
        return [ip.strip() for ip in self.TRUSTED_PROXY_IPS.split(",") if ip.strip()]


settings = Settings()

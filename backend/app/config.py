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
    MONGO_URI: str = ""
    MONGO_DB_NAME: str = "supply_chain_db"

    # --- LLM ---
    LLM_PROVIDER: str = "anthropic"  # anthropic | openai | gemini
    LLM_MODEL: str = "claude-sonnet-4-6"
    LLM_API_KEY: str = ""

    # --- Business rules (REQUIRED by official PS: >$50,000 impact => human approval) ---
    AUTONOMOUS_APPROVAL_LIMIT_USD: float = 50000.0

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- Misc ---
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()

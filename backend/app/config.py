"""
app/config.py
Owner: Developer 2 (Backend / Simulation)

Centralized settings object. Every other module should import `settings` from here
instead of calling os.getenv() directly.

NOTE: LLM logic is handled entirely in the n8n workflow (Groq AI Agent node).
      The backend is a pure CRUD / data API — no LLM keys here.

RECEIVES: values from backend/.env
DELIVERS: a singleton `settings` instance used by database.py, api/, etc.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database (MongoDB Atlas) ---
    MONGO_URI: str = "mongodb://127.0.0.1:27017"
    MONGO_DB_NAME: str = "supplychaindb"

    # --- N8N Integration ---
    N8N_BASE_URL: str = "http://localhost:5678"
    BACKEND_API_KEY: str = "changeme-secret-key"

    # --- Business rules (REQUIRED: >$50,000 impact => human approval) ---
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

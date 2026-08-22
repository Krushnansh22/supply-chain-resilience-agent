"""
app/schemas/config.py

Pydantic response schemas for the /api/v1/config/* endpoints.

N8NConfigResponse is the canonical contract returned to n8n on every
incident lifecycle start. n8n uses it to dynamically substitute email
addresses, approval thresholds, and LLM parameters — eliminating
hard-coded $env references scattered across workflow nodes.
"""

from pydantic import BaseModel, EmailStr, Field


class LLMConfig(BaseModel):
    """Sub-schema for the Groq LLM configuration block."""

    provider: str = Field(..., description="LLM provider identifier (e.g. 'groq')")
    model: str = Field(..., description="Model name passed to the Groq API")
    temperature: float = Field(
        ..., ge=0.0, le=2.0, description="Sampling temperature (0.0–2.0)"
    )


class N8NConfigResponse(BaseModel):
    """
    Configuration payload returned to n8n at the start of each incident lifecycle.

    All fields are strictly typed. Missing or malformed environment variables
    will raise HTTP 500 before this schema is ever instantiated.
    """

    # --- Email addresses ---
    notify_from_email: EmailStr = Field(
        ...,
        description="Sender address for all outbound notification emails",
    )
    approval_notify_email: EmailStr = Field(
        ...,
        description="Recipient for human-approval request emails",
    )
    ops_alert_email: EmailStr = Field(
        ...,
        description="Recipient for critical ops escalation emails",
    )

    # --- Business logic ---
    autonomous_approval_limit_usd: float = Field(
        ...,
        ge=0,
        description=(
            "Recovery plans costing more than this (USD) require human approval"
        ),
    )

    # --- Backend ---
    backend_url: str = Field(
        ...,
        description=(
            "Internal URL n8n uses to call backend APIs "
            "(e.g. http://backend:8000)"
        ),
    )

    # --- LLM ---
    llm_config: LLMConfig = Field(
        ...,
        description="Groq LLM provider, model name, and temperature",
    )

    model_config = {"json_schema_extra": {
        "example": {
            "notify_from_email": "noreply@yourdomain.com",
            "approval_notify_email": "procurement@yourdomain.com",
            "ops_alert_email": "ops-team@yourdomain.com",
            "autonomous_approval_limit_usd": 50000.0,
            "backend_url": "http://backend:8000",
            "llm_config": {
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.1,
            },
        }
    }}

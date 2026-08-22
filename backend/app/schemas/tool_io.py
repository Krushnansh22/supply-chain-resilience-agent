"""
app/schemas/tool_io.py
Owner: Developer 1 (Agent) defines what shape it needs; Developer 2/3 implement to match.

Generic envelope for tool call results so the agent loop and audit logger can handle
every tool uniformly, regardless of which dev implemented the underlying logic.

RECEIVES: return value of every function in app/tools/*.py
DELIVERS: consumed by agent/tool_executor.py, which forwards `summary` to audit logging
          and `data` back into the LLM's next turn as the tool_result content.
"""

from pydantic import BaseModel
from typing import Any, Optional


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: Any = None                 # structured payload for the LLM / frontend
    summary: str                     # human-readable one-liner for audit log & UI
    error: Optional[str] = None

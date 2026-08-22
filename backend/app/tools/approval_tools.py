"""
app/tools/approval_tools.py
Owner: Developer 3 (Decision Engine) supplies the threshold rule; Developer 1 (Agent)
       calls this tool instead of letting the LLM decide autonomously (team doc Section 4:
       "Do NOT make the LLM responsible for critical deterministic business calculations").

REQUIRED by PS: ">$50,000 impact" must be flagged for explicit human coordinator approval.

RECEIVES: cost (float) — total cost of the recommended recovery plan
DELIVERS: requires_approval (bool), consumed by the agent to transition into
          WAITING_APPROVAL state instead of EXECUTING.
"""

from app.config import settings
from app.schemas.tool_io import ToolResult


def check_approval(cost: float) -> ToolResult:
    requires_approval = cost > settings.AUTONOMOUS_APPROVAL_LIMIT_USD
    return ToolResult(
        tool_name="check_approval",
        success=True,
        data={
            "cost": cost,
            "autonomous_limit": settings.AUTONOMOUS_APPROVAL_LIMIT_USD,
            "requires_approval": requires_approval,
        },
        summary=(
            f"Recovery cost ${cost:,.0f} exceeds the ${settings.AUTONOMOUS_APPROVAL_LIMIT_USD:,.0f} "
            f"autonomous limit — human approval required."
            if requires_approval else
            f"Recovery cost ${cost:,.0f} is within the autonomous approval limit."
        ),
    )

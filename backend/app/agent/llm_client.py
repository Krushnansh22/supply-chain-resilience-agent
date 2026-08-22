"""
app/agent/llm_client.py
Owner: Developer 1 (Agent)

Thin wrapper so the rest of agent_loop.py doesn't care which LLM provider is
configured. Default: Anthropic Messages API with tool use.

RECEIVES: settings.LLM_PROVIDER / LLM_MODEL / LLM_API_KEY (app/config.py),
          messages list + tools list (from tool_schemas.py)
DELIVERS: a normalized response object agent_loop.py can inspect for text vs
          tool_use blocks, regardless of provider.
"""

from app.config import settings


def call_llm(messages: list[dict], tools: list[dict], system_prompt: str):
    """
    TODO (Dev1): implement provider branching.

    Anthropic example (pseudo-code, install `anthropic` SDK — already in requirements.txt):

        import anthropic
        client = anthropic.Anthropic(api_key=settings.LLM_API_KEY)
        response = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
            tools=tools,
        )
        return response

    Keep the return type consistent so agent_loop.py can do:
        for block in response.content:
            if block.type == "tool_use": ...
            if block.type == "text": ...

    If LLM_PROVIDER == "openai" or "gemini", translate `tools` schema shape and the
    response shape accordingly — isolate that translation entirely in this file.
    """
    raise NotImplementedError("TODO (Dev1): wire up the configured LLM provider")

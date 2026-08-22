"""
tests/test_agent.py
Owner: Developer 1 (Agent)

TODO: mock llm_client.call_llm() to return scripted tool_use sequences and assert
agent_loop.run_agent_for_incident() drives the state machine correctly, including
the replanning path. This is the highest-value test suite for demo reliability —
prioritize it once agent_loop.py's TODOs are implemented.
"""

import pytest


@pytest.mark.skip(reason="TODO (Dev1): implement once agent_loop.py is functional")
def test_supplier_delay_scenario_reaches_plan_ready():
    ...


@pytest.mark.skip(reason="TODO (Dev1): implement once replanning is wired")
def test_replanning_triggered_when_supplier_becomes_unavailable():
    ...

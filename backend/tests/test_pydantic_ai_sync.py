import asyncio

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_sync import run_agent_sync


@pytest.mark.asyncio
async def test_run_agent_sync_works_with_running_event_loop() -> None:
    agent: Agent[None, str] = Agent(TestModel(), output_type=str)

    # Mimic Temporal activity: call sync helper while a loop is already running.
    result = await asyncio.to_thread(run_agent_sync, agent, "hello")
    assert isinstance(result, str)

    # Direct call from async context must not raise "event loop is already running".
    result2 = run_agent_sync(agent, "hello again")
    assert isinstance(result2, str)

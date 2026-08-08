"""Safe PydanticAI sync helpers for Temporal / FastAPI async contexts."""

from __future__ import annotations

import asyncio
import concurrent.futures
from typing import TypeVar

from pydantic_ai import Agent

T = TypeVar("T")


def run_agent_sync(agent: Agent[None, T], user_prompt: str) -> T:
    """Run ``Agent.run_sync`` even when an event loop is already running.

    Temporal activities and Uvicorn handlers own a loop; ``run_sync`` calls
    ``loop.run_until_complete`` and raises ``RuntimeError: this event loop is
    already running``. Offload to a worker thread in that case.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return agent.run_sync(user_prompt).output

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(lambda: agent.run_sync(user_prompt).output)
        return future.result()

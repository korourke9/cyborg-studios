import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from temporalio.testing import WorkflowEnvironment

from gamebuilder.main import create_app
from gamebuilder.orchestration.application.usecase.fail_project import FailProjectUseCase
from gamebuilder.orchestration.application.usecase.run_story_step import RunStoryStepUseCase
from gamebuilder.orchestration.application.usecase.run_vision_step import RunVisionStepUseCase
from gamebuilder.orchestration.infrastructure.config.container import (
    AppContainer,
    build_container,
    init_database,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.persistence.unit_of_work import (
    create_unit_of_work_factory,
)
from gamebuilder.orchestration.infrastructure.temporal.activities import GameGenerationActivities
from gamebuilder.orchestration.infrastructure.temporal.temporal_runtime import create_worker
from gamebuilder.team.design.application.designers_agent_service import DesignersAgentService
from gamebuilder.team.design.infrastructure.agent.deterministic_design_agent_graph import (
    DeterministicDesignAgentGraph,
)
from gamebuilder.team.story.application.writers_agent_service import WritersAgentService
from gamebuilder.team.story.infrastructure.agent.deterministic_story_agent_graph import (
    DeterministicStoryAgentGraph,
)


@pytest.fixture
async def app(tmp_path: Path) -> AsyncIterator[FastAPI]:
    db_path = tmp_path / "test.db"
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{db_path}",
        temporal_task_queue=f"test-game-generation-{uuid4()}",
        cors_allowed_origins="http://localhost:3000",
        design_agent_mode="deterministic",
    )

    async with await WorkflowEnvironment.start_time_skipping() as env:

        def lifespan_factory(cfg: Settings):
            @asynccontextmanager
            async def lifespan(application: FastAPI) -> AsyncIterator[None]:
                container: AppContainer = await build_container(
                    cfg,
                    temporal_client=env.client,
                    start_worker=False,
                )
                await init_database(container.engine)

                uow_factory = create_unit_of_work_factory(container.session_factory)
                activities = GameGenerationActivities(
                    RunVisionStepUseCase(
                        uow_factory,
                        DesignersAgentService(DeterministicDesignAgentGraph()),
                    ),
                    RunStoryStepUseCase(
                        uow_factory,
                        WritersAgentService(DeterministicStoryAgentGraph()),
                    ),
                    FailProjectUseCase(uow_factory),
                )
                worker = create_worker(
                    env.client,
                    cfg.temporal_task_queue,
                    activities,
                )
                container.worker = worker
                application.state.container = container

                worker_task = asyncio.create_task(worker.run())
                try:
                    yield
                finally:
                    worker_task.cancel()
                    try:
                        await worker_task
                    except asyncio.CancelledError:
                        pass
                    await container.engine.dispose()

            return lifespan

        application = create_app(settings, lifespan_factory=lifespan_factory)
        yield application


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            yield http_client


async def test_welcome(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert response.text == "Welcome to Cyborg Studios API"


async def test_create_then_poll_project_until_done(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/projects",
        json={"prompt": "A tiny robot adventure"},
    )
    assert create_response.status_code == 202
    body = create_response.json()
    project_id = body["projectId"]
    assert project_id
    assert body["status"] == "PENDING"

    done_project = await _wait_for_project_done(client, project_id)
    assert done_project["prompt"] == "A tiny robot adventure"
    assert done_project["status"] == "DONE"
    artifact_types = {artifact["type"] for artifact in done_project["artifacts"]}
    assert artifact_types >= {
        "VISION_DOC",
        "DESIGN_PILLARS",
        "MECHANICS_SPEC",
        "SYSTEMS_SPEC",
        "NARRATIVE_SPEC",
        "EXPERIENCE_MILESTONES",
    }


async def test_get_unknown_project_returns_not_found(client: AsyncClient) -> None:
    response = await client.get(f"/api/projects/{uuid4()}")
    assert response.status_code == 404
    assert "message" in response.json()
    assert response.json()["message"]


async def test_list_projects_sorted_by_updated_at(client: AsyncClient) -> None:
    first = await client.post("/api/projects", json={"prompt": "Older cave game"})
    assert first.status_code == 202
    first_id = first.json()["projectId"]
    await _wait_for_project_done(client, first_id)

    second = await client.post("/api/projects", json={"prompt": "Newer sky game"})
    assert second.status_code == 202
    second_id = second.json()["projectId"]
    await _wait_for_project_done(client, second_id)

    response = await client.get("/api/projects")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) >= 2
    ids = [project["id"] for project in projects]
    assert ids.index(second_id) < ids.index(first_id)
    assert "prompt" in projects[0]
    assert "updatedAt" in projects[0]


async def test_delete_project_removes_project_and_artifacts(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/projects",
        json={"prompt": "Temporary delete me"},
    )
    assert create_response.status_code == 202
    project_id = create_response.json()["projectId"]
    await _wait_for_project_done(client, project_id)

    delete_response = await client.delete(f"/api/projects/{project_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/projects/{project_id}")
    assert get_response.status_code == 404

    listed = await client.get("/api/projects")
    assert project_id not in [project["id"] for project in listed.json()]


async def test_delete_unknown_project_returns_not_found(client: AsyncClient) -> None:
    response = await client.delete(f"/api/projects/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["message"]


async def _wait_for_project_done(client: AsyncClient, project_id: str) -> dict:
    for _ in range(40):
        response = await client.get(f"/api/projects/{project_id}")
        if response.status_code == 200 and response.json()["status"] == "DONE":
            return response.json()
        await asyncio.sleep(0.1)
    raise AssertionError("Project did not reach DONE status in time")

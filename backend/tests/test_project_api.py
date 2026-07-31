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
from gamebuilder.orchestration.application.usecase.run_vision_step import RunVisionStepUseCase
from gamebuilder.orchestration.infrastructure.config.container import (
    AppContainer,
    build_container,
    init_database,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.persistence.artifact_repository import (
    SqlAlchemyArtifactRepository,
)
from gamebuilder.orchestration.infrastructure.persistence.project_repository import (
    SqlAlchemyProjectRepository,
)
from gamebuilder.orchestration.infrastructure.temporal.activities import GameGenerationActivities
from gamebuilder.orchestration.infrastructure.temporal.temporal_runtime import create_worker
from gamebuilder.team.design.application.designers_agent_service import DesignersAgentService
from gamebuilder.team.design.infrastructure.agent.deterministic_design_agent_graph import (
    DeterministicDesignAgentGraph,
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

                project_repository = SqlAlchemyProjectRepository(container.session_factory)
                artifact_repository = SqlAlchemyArtifactRepository(container.session_factory)
                activities = GameGenerationActivities(
                    RunVisionStepUseCase(
                        project_repository,
                        artifact_repository,
                        DesignersAgentService(DeterministicDesignAgentGraph()),
                    ),
                    FailProjectUseCase(project_repository),
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
    }


async def test_get_unknown_project_returns_not_found(client: AsyncClient) -> None:
    response = await client.get(f"/api/projects/{uuid4()}")
    assert response.status_code == 404


async def _wait_for_project_done(client: AsyncClient, project_id: str) -> dict:
    for _ in range(40):
        response = await client.get(f"/api/projects/{project_id}")
        if response.status_code == 200 and response.json()["status"] == "DONE":
            return response.json()
        await asyncio.sleep(0.1)
    raise AssertionError("Project did not reach DONE status in time")

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from temporalio.client import Client
from temporalio.worker import Worker

from gamebuilder.orchestration.application.usecase.create_project import CreateProjectUseCase
from gamebuilder.orchestration.application.usecase.fail_project import FailProjectUseCase
from gamebuilder.orchestration.application.usecase.get_project import GetProjectUseCase
from gamebuilder.orchestration.application.usecase.run_vision_step import RunVisionStepUseCase
from gamebuilder.orchestration.application.usecase.start_project_generation import (
    StartProjectGenerationUseCase,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.persistence.artifact_repository import (
    SqlAlchemyArtifactRepository,
)
from gamebuilder.orchestration.infrastructure.persistence.database import (
    Base,
    create_engine,
    create_session_factory,
)
from gamebuilder.orchestration.infrastructure.persistence.project_repository import (
    SqlAlchemyProjectRepository,
)
from gamebuilder.orchestration.infrastructure.temporal.temporal_runtime import (
    GameGenerationActivities,
    TemporalGenerationWorkflowRunner,
    create_temporal_client,
    create_worker,
)
from gamebuilder.team.design.application.designers_agent_service import DesignersAgentService
from gamebuilder.team.design.infrastructure.agent.deterministic_design_agent_graph import (
    DeterministicDesignAgentGraph,
)


@dataclass
class AppContainer:
    settings: Settings
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    create_project: CreateProjectUseCase
    get_project: GetProjectUseCase
    start_project_generation: StartProjectGenerationUseCase
    temporal_client: Client | None = None
    worker: Worker | None = None


async def build_container(
    settings: Settings | None = None,
    *,
    temporal_client: Client | None = None,
    start_worker: bool = True,
) -> AppContainer:
    settings = settings or Settings()
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    project_repository = SqlAlchemyProjectRepository(session_factory)
    artifact_repository = SqlAlchemyArtifactRepository(session_factory)
    designers = DesignersAgentService(DeterministicDesignAgentGraph())

    run_vision = RunVisionStepUseCase(
        project_repository, artifact_repository, designers
    )
    fail_project = FailProjectUseCase(project_repository)

    client = temporal_client or await create_temporal_client(
        settings.temporal_target, settings.temporal_namespace
    )
    runner = TemporalGenerationWorkflowRunner(client, settings.temporal_task_queue)
    activities = GameGenerationActivities(run_vision, fail_project)

    worker: Worker | None = None
    if start_worker:
        worker = create_worker(client, settings.temporal_task_queue, activities)

    return AppContainer(
        settings=settings,
        engine=engine,
        session_factory=session_factory,
        create_project=CreateProjectUseCase(project_repository),
        get_project=GetProjectUseCase(project_repository, artifact_repository),
        start_project_generation=StartProjectGenerationUseCase(runner),
        temporal_client=client,
        worker=worker,
    )


async def init_database(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

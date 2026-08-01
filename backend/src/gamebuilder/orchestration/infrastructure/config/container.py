from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from temporalio.client import Client
from temporalio.worker import Worker

from gamebuilder.orchestration.application.usecase.create_project import CreateProjectUseCase
from gamebuilder.orchestration.application.usecase.delete_project import DeleteProjectUseCase
from gamebuilder.orchestration.application.usecase.fail_project import FailProjectUseCase
from gamebuilder.orchestration.application.usecase.get_game_bundle_script import (
    GetGameBundleScriptUseCase,
)
from gamebuilder.orchestration.application.usecase.get_project import GetProjectUseCase
from gamebuilder.orchestration.application.usecase.list_projects import ListProjectsUseCase
from gamebuilder.orchestration.application.usecase.run_art_step import RunArtStepUseCase
from gamebuilder.orchestration.application.usecase.run_engineering_step import (
    RunEngineeringStepUseCase,
)
from gamebuilder.orchestration.application.usecase.run_producer_step import (
    RunProducerStepUseCase,
)
from gamebuilder.orchestration.application.usecase.run_qa_step import RunQaStepUseCase
from gamebuilder.orchestration.application.usecase.run_story_step import RunStoryStepUseCase
from gamebuilder.orchestration.application.usecase.run_vision_step import RunVisionStepUseCase
from gamebuilder.orchestration.application.usecase.start_project_generation import (
    StartProjectGenerationUseCase,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.factory import create_llm_router
from gamebuilder.orchestration.infrastructure.persistence.database import (
    Base,
    create_engine,
    create_session_factory,
)
from gamebuilder.orchestration.infrastructure.persistence.unit_of_work import (
    create_unit_of_work_factory,
)
from gamebuilder.orchestration.infrastructure.temporal.activities import GameGenerationActivities
from gamebuilder.orchestration.infrastructure.temporal.temporal_runtime import (
    TemporalGenerationWorkflowRunner,
    create_temporal_client,
    create_worker,
)
from gamebuilder.team.art.application.art_team_agent_service import ArtTeamAgentService
from gamebuilder.team.art.application.port.art_agent_graph import ArtAgentGraph
from gamebuilder.team.art.infrastructure.config.factory import build_art_agent_graph
from gamebuilder.team.design.application.designers_agent_service import DesignersAgentService
from gamebuilder.team.design.application.port.design_agent_graph import DesignAgentGraph
from gamebuilder.team.design.infrastructure.config.factory import build_design_agent_graph
from gamebuilder.team.engineering.application.engineers_agent_service import (
    EngineersAgentService,
)
from gamebuilder.team.engineering.application.port.engineering_agent_graph import (
    EngineeringAgentGraph,
)
from gamebuilder.team.engineering.infrastructure.config.factory import (
    build_engineering_agent_graph,
)
from gamebuilder.team.producer.application.port.producer_agent_graph import (
    ProducerAgentGraph,
)
from gamebuilder.team.producer.application.producer_agent_service import (
    ProducerAgentService,
)
from gamebuilder.team.producer.infrastructure.config.factory import (
    build_producer_agent_graph,
)
from gamebuilder.team.qa.application.port.qa_agent_graph import QaAgentGraph
from gamebuilder.team.qa.application.qa_agent_service import QaAgentService
from gamebuilder.team.qa.infrastructure.config.factory import build_qa_agent_graph
from gamebuilder.team.story.application.port.story_agent_graph import StoryAgentGraph
from gamebuilder.team.story.application.writers_agent_service import WritersAgentService
from gamebuilder.team.story.infrastructure.config.factory import build_story_agent_graph


@dataclass
class AppContainer:
    settings: Settings
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    create_project: CreateProjectUseCase
    list_projects: ListProjectsUseCase
    get_project: GetProjectUseCase
    delete_project: DeleteProjectUseCase
    get_game_bundle_script: GetGameBundleScriptUseCase
    start_project_generation: StartProjectGenerationUseCase
    temporal_client: Client | None = None
    worker: Worker | None = None


async def build_container(
    settings: Settings | None = None,
    *,
    temporal_client: Client | None = None,
    start_worker: bool = True,
    design_agent_graph: DesignAgentGraph | None = None,
    story_agent_graph: StoryAgentGraph | None = None,
    art_agent_graph: ArtAgentGraph | None = None,
    engineering_agent_graph: EngineeringAgentGraph | None = None,
    qa_agent_graph: QaAgentGraph | None = None,
    producer_agent_graph: ProducerAgentGraph | None = None,
) -> AppContainer:
    settings = settings or Settings()
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    uow_factory = create_unit_of_work_factory(session_factory)

    if design_agent_graph is None:
        design_agent_graph = build_design_agent_graph(
            mode=settings.resolve_design_agent_mode(),
            settings=settings,
            llm_router=create_llm_router(settings),
        )
    designers = DesignersAgentService(design_agent_graph)

    if story_agent_graph is None:
        story_agent_graph = build_story_agent_graph(
            mode=settings.resolve_story_agent_mode(),
            settings=settings,
        )
    writers = WritersAgentService(story_agent_graph)

    if art_agent_graph is None:
        art_agent_graph = build_art_agent_graph(
            mode=settings.resolve_art_agent_mode(),
            settings=settings,
        )
    artists = ArtTeamAgentService(art_agent_graph)

    if engineering_agent_graph is None:
        engineering_agent_graph = build_engineering_agent_graph(
            mode=settings.resolve_engineering_agent_mode(),
            settings=settings,
        )
    engineers = EngineersAgentService(engineering_agent_graph)

    if qa_agent_graph is None:
        qa_agent_graph = build_qa_agent_graph(
            mode=settings.resolve_qa_agent_mode(),
            settings=settings,
        )
    qa = QaAgentService(qa_agent_graph)

    if producer_agent_graph is None:
        producer_agent_graph = build_producer_agent_graph(
            mode=settings.resolve_producer_agent_mode(),
            settings=settings,
        )
    producer = ProducerAgentService(producer_agent_graph)

    run_vision = RunVisionStepUseCase(uow_factory, designers)
    run_story = RunStoryStepUseCase(uow_factory, writers)
    run_art = RunArtStepUseCase(uow_factory, artists)
    run_engineering = RunEngineeringStepUseCase(uow_factory, engineers)
    run_qa = RunQaStepUseCase(uow_factory, qa)
    run_producer = RunProducerStepUseCase(uow_factory, producer)
    fail_project = FailProjectUseCase(uow_factory)

    client = temporal_client or await create_temporal_client(
        settings.temporal_target, settings.temporal_namespace
    )
    runner = TemporalGenerationWorkflowRunner(client, settings.temporal_task_queue)
    activities = GameGenerationActivities(
        run_vision,
        run_story,
        run_art,
        run_engineering,
        run_qa,
        run_producer,
        fail_project,
    )

    worker: Worker | None = None
    if start_worker:
        worker = create_worker(client, settings.temporal_task_queue, activities)

    return AppContainer(
        settings=settings,
        engine=engine,
        session_factory=session_factory,
        create_project=CreateProjectUseCase(uow_factory),
        list_projects=ListProjectsUseCase(uow_factory),
        get_project=GetProjectUseCase(uow_factory),
        delete_project=DeleteProjectUseCase(uow_factory),
        get_game_bundle_script=GetGameBundleScriptUseCase(uow_factory),
        start_project_generation=StartProjectGenerationUseCase(runner),
        temporal_client=client,
        worker=worker,
    )


async def init_database(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

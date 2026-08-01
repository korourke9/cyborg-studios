import asyncio
from uuid import UUID

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

from gamebuilder.orchestration.infrastructure.temporal.activities import GameGenerationActivities
from gamebuilder.orchestration.infrastructure.temporal.workflow import GameGenerationWorkflow

# PydanticAI pulls in beartype import hooks; Temporal's workflow sandbox importer
# deadlocks on them unless beartype is loaded via the host importer.
_WORKFLOW_SANDBOX_RESTRICTIONS = SandboxRestrictions.default.with_passthrough_modules(
    "beartype",
)


class TemporalGenerationWorkflowRunner:
    def __init__(self, client: Client, task_queue: str) -> None:
        self._client = client
        self._task_queue = task_queue

    async def start(self, project_id: UUID) -> None:
        await self._client.start_workflow(
            GameGenerationWorkflow.run,
            str(project_id),
            id=f"game-generation-{project_id}",
            task_queue=self._task_queue,
        )


async def create_temporal_client(
    target: str,
    namespace: str,
    *,
    retries: int = 30,
    delay_seconds: float = 2.0,
) -> Client:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return await Client.connect(target, namespace=namespace)
        except Exception as exc:  # noqa: BLE001 - retry any connect failure during startup
            last_error = exc
            if attempt == retries:
                break
            await asyncio.sleep(delay_seconds)
    assert last_error is not None
    raise last_error


def create_worker(
    client: Client,
    task_queue: str,
    activities: GameGenerationActivities,
) -> Worker:
    return Worker(
        client,
        task_queue=task_queue,
        workflows=[GameGenerationWorkflow],
        activities=[
            activities.run_vision_step,
            activities.run_story_step,
            activities.run_art_step,
            activities.fail_project,
        ],
        workflow_runner=SandboxedWorkflowRunner(
            restrictions=_WORKFLOW_SANDBOX_RESTRICTIONS,
        ),
    )

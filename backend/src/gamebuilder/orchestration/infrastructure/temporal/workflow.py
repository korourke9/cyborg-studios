from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

_TEAM_TIMEOUT = timedelta(minutes=15)


@workflow.defn(name="GameGenerationWorkflow")
class GameGenerationWorkflow:
    @workflow.run
    async def run(self, project_id: str) -> None:
        retry = RetryPolicy(maximum_attempts=3)
        try:
            for activity_name in (
                "runVisionStep",
                "runStoryStep",
                "runArtStep",
                "runEngineeringStep",
                "runQaStep",
                "runProducerStep",
            ):
                await workflow.execute_activity(
                    activity_name,
                    project_id,
                    start_to_close_timeout=_TEAM_TIMEOUT,
                    retry_policy=retry,
                )
        except Exception:
            await workflow.execute_activity(
                "failProject",
                project_id,
                start_to_close_timeout=timedelta(minutes=1),
            )
            raise

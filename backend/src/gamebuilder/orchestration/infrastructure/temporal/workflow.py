from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy


@workflow.defn(name="GameGenerationWorkflow")
class GameGenerationWorkflow:
    @workflow.run
    async def run(self, project_id: str) -> None:
        retry = RetryPolicy(maximum_attempts=3)
        try:
            await workflow.execute_activity(
                "runVisionStep",
                project_id,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry,
            )
            await workflow.execute_activity(
                "runStoryStep",
                project_id,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry,
            )
            await workflow.execute_activity(
                "runArtStep",
                project_id,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry,
            )
            await workflow.execute_activity(
                "runEngineeringStep",
                project_id,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry,
            )
        except Exception:
            await workflow.execute_activity(
                "failProject",
                project_id,
                start_to_close_timeout=timedelta(minutes=1),
            )
            raise

from uuid import UUID

from temporalio import activity

from gamebuilder.orchestration.application.usecase.fail_project import FailProjectUseCase
from gamebuilder.orchestration.application.usecase.run_vision_step import RunVisionStepUseCase


class GameGenerationActivities:
    def __init__(
        self,
        run_vision_step_use_case: RunVisionStepUseCase,
        fail_project_use_case: FailProjectUseCase,
    ) -> None:
        self._run_vision_step_use_case = run_vision_step_use_case
        self._fail_project_use_case = fail_project_use_case

    @activity.defn(name="runVisionStep")
    async def run_vision_step(self, project_id: str) -> None:
        await self._run_vision_step_use_case.execute(UUID(project_id))

    @activity.defn(name="failProject")
    async def fail_project(self, project_id: str) -> None:
        await self._fail_project_use_case.execute(UUID(project_id))

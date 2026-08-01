from uuid import UUID

from temporalio import activity

from gamebuilder.orchestration.application.usecase.fail_project import FailProjectUseCase
from gamebuilder.orchestration.application.usecase.run_art_step import RunArtStepUseCase
from gamebuilder.orchestration.application.usecase.run_engineering_step import (
    RunEngineeringStepUseCase,
)
from gamebuilder.orchestration.application.usecase.run_qa_step import RunQaStepUseCase
from gamebuilder.orchestration.application.usecase.run_story_step import RunStoryStepUseCase
from gamebuilder.orchestration.application.usecase.run_vision_step import RunVisionStepUseCase


class GameGenerationActivities:
    def __init__(
        self,
        run_vision_step_use_case: RunVisionStepUseCase,
        run_story_step_use_case: RunStoryStepUseCase,
        run_art_step_use_case: RunArtStepUseCase,
        run_engineering_step_use_case: RunEngineeringStepUseCase,
        run_qa_step_use_case: RunQaStepUseCase,
        fail_project_use_case: FailProjectUseCase,
    ) -> None:
        self._run_vision_step_use_case = run_vision_step_use_case
        self._run_story_step_use_case = run_story_step_use_case
        self._run_art_step_use_case = run_art_step_use_case
        self._run_engineering_step_use_case = run_engineering_step_use_case
        self._run_qa_step_use_case = run_qa_step_use_case
        self._fail_project_use_case = fail_project_use_case

    @activity.defn(name="runVisionStep")
    async def run_vision_step(self, project_id: str) -> None:
        await self._run_vision_step_use_case.execute(UUID(project_id))

    @activity.defn(name="runStoryStep")
    async def run_story_step(self, project_id: str) -> None:
        await self._run_story_step_use_case.execute(UUID(project_id))

    @activity.defn(name="runArtStep")
    async def run_art_step(self, project_id: str) -> None:
        await self._run_art_step_use_case.execute(UUID(project_id))

    @activity.defn(name="runEngineeringStep")
    async def run_engineering_step(self, project_id: str) -> None:
        await self._run_engineering_step_use_case.execute(UUID(project_id))

    @activity.defn(name="runQaStep")
    async def run_qa_step(self, project_id: str) -> None:
        await self._run_qa_step_use_case.execute(UUID(project_id))

    @activity.defn(name="failProject")
    async def fail_project(self, project_id: str) -> None:
        await self._fail_project_use_case.execute(UUID(project_id))

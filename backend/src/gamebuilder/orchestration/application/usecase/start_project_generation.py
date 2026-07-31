from uuid import UUID

from gamebuilder.orchestration.application.port.generation_workflow_runner import (
    GenerationWorkflowRunner,
)


class StartProjectGenerationUseCase:
    def __init__(self, generation_workflow_runner: GenerationWorkflowRunner) -> None:
        self._generation_workflow_runner = generation_workflow_runner

    async def execute(self, project_id: UUID) -> None:
        await self._generation_workflow_runner.start(project_id)

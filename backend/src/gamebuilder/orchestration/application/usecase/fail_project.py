from uuid import UUID

from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.orchestration.domain.repository.project_repository import ProjectRepository


class FailProjectUseCase:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(self, project_id: UUID) -> None:
        await self._project_repository.update_status(project_id, ProjectStatus.FAILED)

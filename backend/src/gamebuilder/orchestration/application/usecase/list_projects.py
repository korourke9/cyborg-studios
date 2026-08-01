from gamebuilder.orchestration.domain.model.project import Project
from gamebuilder.orchestration.domain.repository.project_repository import ProjectRepository


class ListProjectsUseCase:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(self) -> list[Project]:
        return await self._project_repository.list_recent()

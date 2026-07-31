from time import time
from uuid import uuid4

from gamebuilder.orchestration.domain.model.project import Project
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.orchestration.domain.repository.project_repository import ProjectRepository


class CreateProjectUseCase:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(self, prompt: str) -> Project:
        now = int(time() * 1000)
        project = Project(
            id=uuid4(),
            prompt=prompt,
            status=ProjectStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        return await self._project_repository.save(project)

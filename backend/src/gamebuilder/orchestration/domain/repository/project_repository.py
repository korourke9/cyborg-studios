from typing import Protocol
from uuid import UUID

from gamebuilder.orchestration.domain.model.project import Project
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus


class ProjectRepository(Protocol):
    async def save(self, project: Project) -> Project: ...

    async def find_by_id(self, project_id: UUID) -> Project | None: ...

    async def update_status(self, project_id: UUID, status: ProjectStatus) -> None: ...

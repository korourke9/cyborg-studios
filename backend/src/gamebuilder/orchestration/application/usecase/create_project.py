from time import time
from uuid import uuid4

from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.project import Project
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus


class CreateProjectUseCase:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def execute(self, prompt: str) -> Project:
        now = int(time() * 1000)
        project = Project(
            id=uuid4(),
            prompt=prompt,
            status=ProjectStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        async with self._uow_factory() as uow:
            return await uow.projects.save(project)

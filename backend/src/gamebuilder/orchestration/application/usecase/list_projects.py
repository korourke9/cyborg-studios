from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.project import Project


class ListProjectsUseCase:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def execute(self) -> list[Project]:
        async with self._uow_factory() as uow:
            return await uow.projects.list_recent()

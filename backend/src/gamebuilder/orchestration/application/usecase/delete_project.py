from uuid import UUID

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory


class DeleteProjectUseCase:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def execute(self, project_id: UUID) -> None:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "That game could not be found. It may have already been deleted."
                )
            await uow.artifacts.delete_by_project_id(project_id)
            await uow.projects.delete(project_id)

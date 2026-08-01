from uuid import UUID

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.project import Project


class ProjectDetails:
    def __init__(self, project: Project, artifacts: list[Artifact]) -> None:
        self.project = project
        self.artifacts = artifacts


class GetProjectUseCase:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def execute(self, project_id: UUID) -> ProjectDetails:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "That game could not be found. It may have been deleted."
                )
            artifacts = await uow.artifacts.find_by_project_id(project_id)
            return ProjectDetails(project=project, artifacts=artifacts)

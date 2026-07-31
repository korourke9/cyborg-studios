from dataclasses import dataclass
from uuid import UUID

from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.project import Project
from gamebuilder.orchestration.domain.repository.artifact_repository import ArtifactRepository
from gamebuilder.orchestration.domain.repository.project_repository import ProjectRepository


@dataclass(frozen=True)
class ProjectDetails:
    project: Project
    artifacts: list[Artifact]


class GetProjectUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        artifact_repository: ArtifactRepository,
    ) -> None:
        self._project_repository = project_repository
        self._artifact_repository = artifact_repository

    async def execute(self, project_id: UUID) -> ProjectDetails | None:
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            return None
        artifacts = await self._artifact_repository.find_by_project_id(project_id)
        return ProjectDetails(project=project, artifacts=artifacts)

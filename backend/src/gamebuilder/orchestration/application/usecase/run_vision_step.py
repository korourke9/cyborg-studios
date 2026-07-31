from time import time
from uuid import UUID, uuid4

from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.orchestration.domain.repository.artifact_repository import ArtifactRepository
from gamebuilder.orchestration.domain.repository.project_repository import ProjectRepository
from gamebuilder.team.design.application.designers_agent_service import DesignersAgentService
from gamebuilder.team.design.domain.model import DesignTeamOutput


class RunVisionStepUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        artifact_repository: ArtifactRepository,
        designers_agent_service: DesignersAgentService,
    ) -> None:
        self._project_repository = project_repository
        self._artifact_repository = artifact_repository
        self._designers_agent_service = designers_agent_service

    async def execute(self, project_id: UUID) -> None:
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            return

        await self._project_repository.update_status(
            project_id, ProjectStatus.VISION_IN_PROGRESS
        )

        design_output = self._designers_agent_service.generate_initial_design(project.prompt)
        await self._artifact_repository.save(
            self._vision_artifact(project_id, design_output)
        )

        await self._project_repository.update_status(project_id, ProjectStatus.VISION_DONE)
        await self._project_repository.update_status(
            project_id, ProjectStatus.DESIGN_IN_PROGRESS
        )

        for artifact in self._design_artifacts(project_id, design_output):
            await self._artifact_repository.save(artifact)

        await self._project_repository.update_status(project_id, ProjectStatus.DESIGN_DONE)
        await self._project_repository.update_status(project_id, ProjectStatus.DONE)

    def _vision_artifact(self, project_id: UUID, output: DesignTeamOutput) -> Artifact:
        return Artifact(
            id=uuid4(),
            project_id=project_id,
            type=ArtifactType.VISION_DOC,
            payload=output.vision_doc.model_dump_json(by_alias=True),
            created_at=int(time() * 1000),
        )

    def _design_artifacts(
        self, project_id: UUID, output: DesignTeamOutput
    ) -> list[Artifact]:
        now = int(time() * 1000)
        return [
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.DESIGN_PILLARS,
                payload=output.design_pillars.model_dump_json(by_alias=True),
                created_at=now,
            ),
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.MECHANICS_SPEC,
                payload=output.mechanics_spec.model_dump_json(by_alias=True),
                created_at=now,
            ),
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.SYSTEMS_SPEC,
                payload=output.systems_spec.model_dump_json(by_alias=True),
                created_at=now,
            ),
        ]

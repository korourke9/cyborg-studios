from time import time
from uuid import UUID, uuid4

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.team.design.application.designers_agent_service import DesignersAgentService
from gamebuilder.team.design.domain.model import DesignTeamOutput


class RunVisionStepUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        designers_agent_service: DesignersAgentService,
    ) -> None:
        self._uow_factory = uow_factory
        self._designers_agent_service = designers_agent_service

    async def execute(self, project_id: UUID) -> None:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Design could not start because that game no longer exists."
                )
            prompt = project.prompt
            await uow.projects.update_status(
                project_id, ProjectStatus.VISION_IN_PROGRESS
            )

        design_output = self._designers_agent_service.generate_initial_design(prompt)

        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Design finished but the game was deleted before results "
                    "could be saved."
                )
            await uow.artifacts.save(self._vision_artifact(project_id, design_output))
            await uow.projects.update_status(project_id, ProjectStatus.VISION_DONE)
            await uow.projects.update_status(
                project_id, ProjectStatus.DESIGN_IN_PROGRESS
            )
            for artifact in self._design_artifacts(project_id, design_output):
                await uow.artifacts.save(artifact)
            await uow.projects.update_status(project_id, ProjectStatus.DESIGN_DONE)

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

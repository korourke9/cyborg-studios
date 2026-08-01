import json
from time import time
from uuid import UUID, uuid4

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.team.art.application.art_team_agent_service import ArtTeamAgentService
from gamebuilder.team.art.domain.model import ArtTeamInput, ArtTeamOutput


class RunArtStepUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        art_team_agent_service: ArtTeamAgentService,
    ) -> None:
        self._uow_factory = uow_factory
        self._art_team_agent_service = art_team_agent_service

    async def execute(self, project_id: UUID) -> None:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Art could not start because that game no longer exists."
                )
            artifacts = await uow.artifacts.find_by_project_id(project_id)
            art_input = self._build_input(project.prompt, artifacts)
            await uow.projects.update_status(project_id, ProjectStatus.ART_IN_PROGRESS)

        art_output = self._art_team_agent_service.generate_art(art_input)

        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Art finished but the game was deleted before results "
                    "could be saved."
                )
            for artifact in self._art_artifacts(project_id, art_output):
                await uow.artifacts.save(artifact)
            await uow.projects.update_status(project_id, ProjectStatus.ART_DONE)
            await uow.projects.update_status(project_id, ProjectStatus.DONE)

    def _build_input(self, prompt: str, artifacts: list[Artifact]) -> ArtTeamInput:
        vision_summary = ""
        target_mood = ""
        narrative_tone = ""
        setting = ""

        for artifact in artifacts:
            try:
                payload = json.loads(artifact.payload)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            if artifact.type == ArtifactType.VISION_DOC:
                vision_summary = str(payload.get("summary") or "")
                target_mood = str(
                    payload.get("targetMood") or payload.get("target_mood") or ""
                )
            if artifact.type == ArtifactType.NARRATIVE_SPEC:
                narrative_tone = str(payload.get("tone") or "")
                setting = str(payload.get("setting") or "")

        return ArtTeamInput(
            prompt=prompt,
            vision_summary=vision_summary,
            target_mood=target_mood,
            narrative_tone=narrative_tone,
            setting=setting,
        )

    def _art_artifacts(self, project_id: UUID, output: ArtTeamOutput) -> list[Artifact]:
        now = int(time() * 1000)
        return [
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.ART_DIRECTION,
                payload=output.art_direction.model_dump_json(by_alias=True),
                created_at=now,
            ),
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.ASSET_LIST,
                payload=output.asset_list.model_dump_json(by_alias=True),
                created_at=now,
            ),
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.ASSET_PROMPTS,
                payload=output.asset_prompts.model_dump_json(by_alias=True),
                created_at=now,
            ),
        ]

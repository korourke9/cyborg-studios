import json
from time import time
from uuid import UUID, uuid4

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.team.engineering.application.engineers_agent_service import (
    EngineersAgentService,
)
from gamebuilder.team.engineering.domain.model import (
    EngineeringTeamInput,
    EngineeringTeamOutput,
)


class RunEngineeringStepUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        engineers_agent_service: EngineersAgentService,
    ) -> None:
        self._uow_factory = uow_factory
        self._engineers_agent_service = engineers_agent_service

    async def execute(self, project_id: UUID) -> None:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Engineering could not start because that game no longer exists."
                )
            artifacts = await uow.artifacts.find_by_project_id(project_id)
            eng_input = self._build_input(project.prompt, artifacts)
            await uow.projects.update_status(
                project_id, ProjectStatus.ENGINEERING_IN_PROGRESS
            )

        eng_output = self._engineers_agent_service.generate_bundle(eng_input)

        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Engineering finished but the game was deleted before "
                    "results could be saved."
                )
            for artifact in self._engineering_artifacts(project_id, eng_output):
                await uow.artifacts.save(artifact)
            await uow.projects.update_status(
                project_id, ProjectStatus.ENGINEERING_DONE
            )

    def _build_input(
        self, prompt: str, artifacts: list[Artifact]
    ) -> EngineeringTeamInput:
        vision_summary = ""
        core_loop = ""
        narrative_tone = ""
        setting = ""
        art_style = ""
        background_hex = "#fff4e8"
        player_hex = "#9b7ed9"
        platform_hex = "#3a2a4a"
        goal_hex = "#ff8c42"

        for artifact in artifacts:
            try:
                payload = json.loads(artifact.payload)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            if artifact.type == ArtifactType.VISION_DOC:
                vision_summary = str(payload.get("summary") or "")
            if artifact.type == ArtifactType.MECHANICS_SPEC:
                core_loop = str(
                    payload.get("coreLoop") or payload.get("core_loop") or ""
                )
            if artifact.type == ArtifactType.NARRATIVE_SPEC:
                narrative_tone = str(payload.get("tone") or "")
                setting = str(payload.get("setting") or "")
            if artifact.type == ArtifactType.ART_DIRECTION:
                art_style = str(payload.get("style") or "")
                palette = payload.get("palette")
                if isinstance(palette, list):
                    by_role = {
                        str(item.get("role") or "").lower(): str(item.get("hex") or "")
                        for item in palette
                        if isinstance(item, dict)
                    }
                    background_hex = by_role.get("background") or background_hex
                    player_hex = by_role.get("primary") or player_hex
                    platform_hex = by_role.get("ink") or platform_hex
                    goal_hex = by_role.get("secondary") or by_role.get("accent") or goal_hex

        return EngineeringTeamInput(
            prompt=prompt,
            vision_summary=vision_summary,
            core_loop=core_loop,
            narrative_tone=narrative_tone,
            setting=setting,
            art_style=art_style,
            background_hex=background_hex,
            player_hex=player_hex,
            platform_hex=platform_hex,
            goal_hex=goal_hex,
        )

    def _engineering_artifacts(
        self, project_id: UUID, output: EngineeringTeamOutput
    ) -> list[Artifact]:
        now = int(time() * 1000)
        return [
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.GAME_BUNDLE,
                payload=output.game_bundle.model_dump_json(by_alias=True),
                created_at=now,
            )
        ]

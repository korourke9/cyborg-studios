import asyncio
import json
from pathlib import Path
from time import time
from uuid import UUID, uuid4

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.image_generator import ImageGenerator
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.application.team_agent_spec import ResolvedAgentRuntime
from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.team.art.application.art_team_agent_service import ArtTeamAgentService
from gamebuilder.team.art.application.materialize_images import materialize_art_images
from gamebuilder.team.art.domain.model import ArtTeamInput, ArtTeamOutput


class RunArtStepUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        art_team_agent_service: ArtTeamAgentService,
        *,
        art_runtime: ResolvedAgentRuntime,
        image_generator: ImageGenerator | None = None,
        asset_root: Path,
        image_size: str = "512x512",
        image_soft_fail: bool = True,
        public_api_base_url: str = "http://localhost:8080",
    ) -> None:
        self._uow_factory = uow_factory
        self._art_team_agent_service = art_team_agent_service
        self._art_runtime = art_runtime
        self._image_generator = image_generator
        self._asset_root = asset_root
        self._image_size = image_size
        self._image_soft_fail = image_soft_fail
        self._public_api_base_url = public_api_base_url

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

        def _generate_and_materialize() -> tuple[
            ArtTeamOutput, list[tuple[str, str, Path, str]]
        ]:
            output = self._art_team_agent_service.generate_art(art_input)
            return materialize_art_images(
                project_id=project_id,
                art_output=output,
                runtime=self._art_runtime,
                image_generator=self._image_generator,
                asset_root=self._asset_root,
                size=self._image_size,
                soft_fail=self._image_soft_fail,
                public_api_base_url=self._public_api_base_url,
                game_prompt=art_input.prompt,
            )

        art_output, binaries = await asyncio.to_thread(_generate_and_materialize)

        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Art finished but the game was deleted before results "
                    "could be saved."
                )
            for artifact in self._art_artifacts(project_id, art_output, binaries):
                await uow.artifacts.save(artifact)
            await uow.projects.update_status(project_id, ProjectStatus.ART_DONE)

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

    def _art_artifacts(
        self,
        project_id: UUID,
        output: ArtTeamOutput,
        binaries: list[tuple[str, str, Path, str]],
    ) -> list[Artifact]:
        now = int(time() * 1000)
        artifacts = [
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
        for asset_id, role, path, content_type in binaries:
            payload = json.dumps(
                {
                    "assetId": asset_id,
                    "role": role,
                    "filePath": str(path),
                    "contentType": content_type,
                    "fileRef": f"/api/projects/{project_id}/assets/{asset_id}",
                }
            )
            artifacts.append(
                Artifact(
                    id=uuid4(),
                    project_id=project_id,
                    type=ArtifactType.BINARY_ASSET,
                    payload=payload,
                    created_at=now,
                )
            )
        return artifacts

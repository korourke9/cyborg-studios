import asyncio
import json
from time import time
from uuid import UUID, uuid4

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.team.story.application.writers_agent_service import WritersAgentService
from gamebuilder.team.story.domain.model import StoryTeamInput, StoryTeamOutput


class RunStoryStepUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        writers_agent_service: WritersAgentService,
    ) -> None:
        self._uow_factory = uow_factory
        self._writers_agent_service = writers_agent_service

    async def execute(self, project_id: UUID) -> None:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Story could not start because that game no longer exists."
                )
            artifacts = await uow.artifacts.find_by_project_id(project_id)
            story_input = self._build_input(project.prompt, artifacts)
            await uow.projects.update_status(
                project_id, ProjectStatus.STORY_IN_PROGRESS
            )

        story_output = await asyncio.to_thread(
            self._writers_agent_service.generate_story, story_input
        )

        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Story finished but the game was deleted before results "
                    "could be saved."
                )
            for artifact in self._story_artifacts(project_id, story_output):
                await uow.artifacts.save(artifact)
            await uow.projects.update_status(project_id, ProjectStatus.STORY_DONE)

    def _build_input(self, prompt: str, artifacts: list[Artifact]) -> StoryTeamInput:
        vision_summary = ""
        player_fantasy = ""
        pillars: list[str] = []

        for artifact in artifacts:
            try:
                payload = json.loads(artifact.payload)
            except json.JSONDecodeError:
                continue
            if artifact.type == ArtifactType.VISION_DOC and isinstance(payload, dict):
                vision_summary = str(payload.get("summary") or "")
                player_fantasy = str(
                    payload.get("playerFantasy") or payload.get("player_fantasy") or ""
                )
            if artifact.type == ArtifactType.DESIGN_PILLARS and isinstance(payload, dict):
                raw = payload.get("pillars") or []
                if isinstance(raw, list):
                    pillars = [str(item) for item in raw]

        return StoryTeamInput(
            prompt=prompt,
            vision_summary=vision_summary,
            design_pillars=tuple(pillars),
            player_fantasy=player_fantasy,
        )

    def _story_artifacts(
        self, project_id: UUID, output: StoryTeamOutput
    ) -> list[Artifact]:
        now = int(time() * 1000)
        return [
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.NARRATIVE_SPEC,
                payload=output.narrative_spec.model_dump_json(by_alias=True),
                created_at=now,
            ),
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.EXPERIENCE_MILESTONES,
                payload=output.experience_milestones.model_dump_json(by_alias=True),
                created_at=now,
            ),
        ]

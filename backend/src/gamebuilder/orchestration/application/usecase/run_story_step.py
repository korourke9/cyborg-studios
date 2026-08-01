import json
from time import time
from uuid import UUID, uuid4

from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.orchestration.domain.repository.artifact_repository import ArtifactRepository
from gamebuilder.orchestration.domain.repository.project_repository import ProjectRepository
from gamebuilder.team.story.application.writers_agent_service import WritersAgentService
from gamebuilder.team.story.domain.model import StoryTeamInput, StoryTeamOutput


class RunStoryStepUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        artifact_repository: ArtifactRepository,
        writers_agent_service: WritersAgentService,
    ) -> None:
        self._project_repository = project_repository
        self._artifact_repository = artifact_repository
        self._writers_agent_service = writers_agent_service

    async def execute(self, project_id: UUID) -> None:
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            return

        await self._project_repository.update_status(
            project_id, ProjectStatus.STORY_IN_PROGRESS
        )

        artifacts = await self._artifact_repository.find_by_project_id(project_id)
        story_input = self._build_input(project.prompt, artifacts)
        story_output = self._writers_agent_service.generate_story(story_input)

        for artifact in self._story_artifacts(project_id, story_output):
            await self._artifact_repository.save(artifact)

        await self._project_repository.update_status(project_id, ProjectStatus.STORY_DONE)
        await self._project_repository.update_status(project_id, ProjectStatus.DONE)

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

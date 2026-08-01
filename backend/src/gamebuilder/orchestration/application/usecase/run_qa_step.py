import json
from time import time
from uuid import UUID, uuid4

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.team.qa.application.qa_agent_service import QaAgentService
from gamebuilder.team.qa.domain.model import QaTeamInput, QaTeamOutput


class RunQaStepUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        qa_agent_service: QaAgentService,
    ) -> None:
        self._uow_factory = uow_factory
        self._qa_agent_service = qa_agent_service

    async def execute(self, project_id: UUID) -> None:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "QA could not start because that game no longer exists."
                )
            artifacts = await uow.artifacts.find_by_project_id(project_id)
            qa_input = self._build_input(project.prompt, artifacts)
            await uow.projects.update_status(project_id, ProjectStatus.QA_IN_PROGRESS)

        qa_output = self._qa_agent_service.review(qa_input)

        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "QA finished but the game was deleted before results "
                    "could be saved."
                )
            for artifact in self._qa_artifacts(project_id, qa_output):
                await uow.artifacts.save(artifact)
            await uow.projects.update_status(project_id, ProjectStatus.QA_DONE)

    def _build_input(self, prompt: str, artifacts: list[Artifact]) -> QaTeamInput:
        vision_summary = ""
        core_loop = ""
        milestones: list[str] = []
        bundle_title = ""
        bundle_summary = ""
        bundle_implemented: list[str] = []
        platform_count = 0
        has_entry_source = False
        player_start = (0, 0)
        goal = (0, 0, 0, 0)

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
            if artifact.type == ArtifactType.EXPERIENCE_MILESTONES:
                raw = payload.get("milestones")
                if isinstance(raw, list):
                    milestones = [str(item) for item in raw]
            if artifact.type == ArtifactType.GAME_BUNDLE:
                bundle_title = str(payload.get("title") or "")
                bundle_summary = str(payload.get("summary") or "")
                impl = payload.get("implemented")
                if isinstance(impl, list):
                    bundle_implemented = [str(item) for item in impl]
                platforms = payload.get("platforms")
                if isinstance(platforms, list):
                    platform_count = len(platforms)
                source = payload.get("entrySource") or payload.get("entry_source")
                has_entry_source = isinstance(source, str) and bool(source.strip())
                player_start = (
                    int(payload.get("playerStartX") or payload.get("player_start_x") or 0),
                    int(payload.get("playerStartY") or payload.get("player_start_y") or 0),
                )
                goal_obj = payload.get("goal")
                if isinstance(goal_obj, dict):
                    goal = (
                        int(goal_obj.get("x") or 0),
                        int(goal_obj.get("y") or 0),
                        int(goal_obj.get("w") or 0),
                        int(goal_obj.get("h") or 0),
                    )

        return QaTeamInput(
            prompt=prompt,
            vision_summary=vision_summary,
            core_loop=core_loop,
            experience_milestones=tuple(milestones),
            bundle_title=bundle_title,
            bundle_summary=bundle_summary,
            bundle_implemented=tuple(bundle_implemented),
            platform_count=platform_count,
            has_entry_source=has_entry_source,
            player_start=player_start,
            goal=goal,
        )

    def _qa_artifacts(self, project_id: UUID, output: QaTeamOutput) -> list[Artifact]:
        now = int(time() * 1000)
        return [
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.QA_ISSUES,
                payload=output.qa_issues.model_dump_json(by_alias=True),
                created_at=now,
            )
        ]

import asyncio
import json
from time import time
from uuid import UUID, uuid4

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.team.producer.application.producer_agent_service import (
    ProducerAgentService,
)
from gamebuilder.team.producer.domain.model import ProducerTeamInput, ProducerTeamOutput


class RunProducerStepUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        producer_agent_service: ProducerAgentService,
    ) -> None:
        self._uow_factory = uow_factory
        self._producer_agent_service = producer_agent_service

    async def execute(self, project_id: UUID) -> None:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Producer could not start because that game no longer exists."
                )
            artifacts = await uow.artifacts.find_by_project_id(project_id)
            producer_input = self._build_input(project.prompt, artifacts)
            await uow.projects.update_status(
                project_id, ProjectStatus.PRODUCER_IN_PROGRESS
            )

        producer_output = await asyncio.to_thread(
            self._producer_agent_service.review, producer_input
        )

        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "Producer finished but the game was deleted before "
                    "results could be saved."
                )
            for artifact in self._producer_artifacts(project_id, producer_output):
                await uow.artifacts.save(artifact)
            await uow.projects.update_status(project_id, ProjectStatus.PRODUCER_DONE)
            await uow.projects.update_status(project_id, ProjectStatus.DONE)

    def _build_input(
        self, prompt: str, artifacts: list[Artifact]
    ) -> ProducerTeamInput:
        vision_summary = ""
        pillars: list[str] = []
        core_loop = ""
        narrative_tone = ""
        setting = ""
        art_mood = ""
        bundle_title = ""
        bundle_summary = ""
        qa_verdict = ""
        qa_summary = ""
        qa_issue_count = 0

        for artifact in artifacts:
            try:
                payload = json.loads(artifact.payload)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            if artifact.type == ArtifactType.VISION_DOC:
                vision_summary = str(payload.get("summary") or "")
            if artifact.type == ArtifactType.DESIGN_PILLARS:
                raw = payload.get("pillars")
                if isinstance(raw, list):
                    pillars = [str(item) for item in raw]
            if artifact.type == ArtifactType.MECHANICS_SPEC:
                core_loop = str(
                    payload.get("coreLoop") or payload.get("core_loop") or ""
                )
            if artifact.type == ArtifactType.NARRATIVE_SPEC:
                narrative_tone = str(payload.get("tone") or "")
                setting = str(payload.get("setting") or "")
            if artifact.type == ArtifactType.ART_DIRECTION:
                art_mood = str(payload.get("mood") or "")
            if artifact.type == ArtifactType.GAME_BUNDLE:
                bundle_title = str(payload.get("title") or "")
                bundle_summary = str(payload.get("summary") or "")
            if artifact.type == ArtifactType.QA_ISSUES:
                qa_verdict = str(payload.get("verdict") or "")
                qa_summary = str(payload.get("summary") or "")
                issues = payload.get("issues")
                if isinstance(issues, list):
                    qa_issue_count = len(issues)

        return ProducerTeamInput(
            prompt=prompt,
            vision_summary=vision_summary,
            design_pillars=tuple(pillars),
            core_loop=core_loop,
            narrative_tone=narrative_tone,
            setting=setting,
            art_mood=art_mood,
            bundle_title=bundle_title,
            bundle_summary=bundle_summary,
            qa_verdict=qa_verdict,
            qa_summary=qa_summary,
            qa_issue_count=qa_issue_count,
        )

    def _producer_artifacts(
        self, project_id: UUID, output: ProducerTeamOutput
    ) -> list[Artifact]:
        now = int(time() * 1000)
        return [
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.COHERENCE_REVIEW,
                payload=output.coherence_review.model_dump_json(by_alias=True),
                created_at=now,
            ),
            Artifact(
                id=uuid4(),
                project_id=project_id,
                type=ArtifactType.PRODUCER_NOTES,
                payload=output.producer_notes.model_dump_json(by_alias=True),
                created_at=now,
            ),
        ]

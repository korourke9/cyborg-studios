import json
from dataclasses import dataclass
from uuid import UUID

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.team.engineering.application.lab_options import (
    DEFAULT_LAB_OPTIONS,
    EngineeringLabOptions,
)


@dataclass(frozen=True)
class PlayBundleInfo:
    project_id: UUID
    title: str
    runtimes: list[str]
    sdk_review_verdict: str
    sdk_review_notes: list[str]
    implemented: list[str]


class GetPlayBundleInfoUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        lab_options: EngineeringLabOptions | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._lab = lab_options or DEFAULT_LAB_OPTIONS

    async def execute(self, project_id: UUID) -> PlayBundleInfo:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError("That game no longer exists.")
            artifacts = await uow.artifacts.find_by_project_id(project_id)

        for artifact in reversed(artifacts):
            if artifact.type != ArtifactType.GAME_BUNDLE:
                continue
            try:
                payload = json.loads(artifact.payload)
            except json.JSONDecodeError as exc:
                raise NotFoundError("Game bundle is damaged.") from exc
            if not isinstance(payload, dict):
                raise NotFoundError("Game bundle is damaged.")

            entry = payload.get("entrySource") or payload.get("entry_source") or ""
            sdk = payload.get("sdkSource") or payload.get("sdk_source") or ""
            verdict = str(
                payload.get("sdkReviewVerdict")
                or payload.get("sdk_review_verdict")
                or "pending"
            ).lower()
            notes_raw = (
                payload.get("sdkReviewNotes") or payload.get("sdk_review_notes") or []
            )
            notes = [str(n) for n in notes_raw] if isinstance(notes_raw, list) else []
            implemented_raw = payload.get("implemented") or []
            implemented = (
                [str(x) for x in implemented_raw]
                if isinstance(implemented_raw, list)
                else []
            )

            runtimes: list[str] = []
            if isinstance(entry, str) and entry.strip():
                runtimes.append("ir")
            has_sdk = isinstance(sdk, str) and bool(sdk.strip())
            if has_sdk and (
                verdict == "allow" or self._lab.allow_unreviewed_sdk_play
            ):
                runtimes.append("sdk")

            return PlayBundleInfo(
                project_id=project_id,
                title=str(payload.get("title") or "Playable build"),
                runtimes=runtimes,
                sdk_review_verdict=verdict,
                sdk_review_notes=notes,
                implemented=implemented,
            )

        raise NotFoundError("No GameBundle yet.")

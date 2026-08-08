import json
from uuid import UUID

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.team.engineering.application.lab_options import (
    DEFAULT_LAB_OPTIONS,
    EngineeringLabOptions,
)


class GetGameBundleScriptUseCase:
    """Return IR-compiled or SDK entry script for a project's GAME_BUNDLE."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        lab_options: EngineeringLabOptions | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._lab = lab_options or DEFAULT_LAB_OPTIONS

    async def execute(self, project_id: UUID, *, runtime: str = "ir") -> str:
        runtime = (runtime or "ir").strip().lower()
        if runtime not in {"ir", "sdk"}:
            raise NotFoundError(f"Unknown play runtime {runtime!r}.")

        payload = await self._latest_bundle_payload(project_id)

        if runtime == "sdk":
            verdict = str(
                payload.get("sdkReviewVerdict") or payload.get("sdk_review_verdict") or ""
            ).lower()
            source = payload.get("sdkSource") or payload.get("sdk_source")
            if not (isinstance(source, str) and source.strip()):
                raise NotFoundError("This game has no SDK script.")
            if verdict != "allow" and not self._lab.allow_unreviewed_sdk_play:
                raise NotFoundError(
                    "SDK runtime is not cleared by security review yet."
                )
            return source

        source = payload.get("entrySource") or payload.get("entry_source")
        if isinstance(source, str) and source.strip():
            return source
        raise NotFoundError("This game's bundle has no playable IR script yet.")

    async def _latest_bundle_payload(self, project_id: UUID) -> dict:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError(
                    "That game no longer exists, so there is nothing to play."
                )
            artifacts = await uow.artifacts.find_by_project_id(project_id)

        for artifact in reversed(artifacts):
            if artifact.type != ArtifactType.GAME_BUNDLE:
                continue
            try:
                payload = json.loads(artifact.payload)
            except json.JSONDecodeError as exc:
                raise NotFoundError(
                    "This game's bundle is damaged and cannot be played."
                ) from exc
            if not isinstance(payload, dict):
                raise NotFoundError(
                    "This game's bundle is damaged and cannot be played."
                )
            return payload

        raise NotFoundError(
            "Play is not ready yet — Engineering has not shipped a GameBundle."
        )

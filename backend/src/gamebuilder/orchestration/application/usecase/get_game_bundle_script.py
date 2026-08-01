import json
from uuid import UUID

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType


class GetGameBundleScriptUseCase:
    """Return the compiled Phaser entrySource for a project's GAME_BUNDLE."""

    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def execute(self, project_id: UUID) -> str:
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
            source = payload.get("entrySource") or payload.get("entry_source")
            if isinstance(source, str) and source.strip():
                return source
            raise NotFoundError(
                "This game's bundle has no playable script yet."
            )

        raise NotFoundError(
            "Play is not ready yet — Engineering has not shipped a GameBundle."
        )

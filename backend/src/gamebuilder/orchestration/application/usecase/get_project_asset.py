import json
from pathlib import Path
from uuid import UUID

from gamebuilder.orchestration.application.errors import NotFoundError
from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWorkFactory
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType


class GetProjectAssetUseCase:
    def __init__(self, uow_factory: UnitOfWorkFactory, asset_root: Path) -> None:
        self._uow_factory = uow_factory
        self._asset_root = asset_root.resolve()

    async def execute(self, project_id: UUID, asset_id: str) -> tuple[bytes, str]:
        async with self._uow_factory() as uow:
            project = await uow.projects.find_by_id(project_id)
            if project is None:
                raise NotFoundError("That game no longer exists.")
            artifacts = await uow.artifacts.find_by_project_id(project_id)

        for artifact in reversed(artifacts):
            if artifact.type != ArtifactType.BINARY_ASSET:
                continue
            try:
                payload = json.loads(artifact.payload)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            if str(payload.get("assetId") or "") != asset_id:
                continue
            file_path = Path(str(payload.get("filePath") or ""))
            content_type = str(payload.get("contentType") or "image/png")
            if not file_path.is_file():
                # Fall back to conventional storage location
                file_path = self._asset_root / str(project_id) / f"{asset_id}.png"
            resolved = file_path.resolve()
            if not str(resolved).startswith(str(self._asset_root)):
                # Allow absolute paths written under asset root only
                if self._asset_root not in resolved.parents and resolved != self._asset_root:
                    # Still allow if file exists from materialize under asset_root
                    alt = self._asset_root / str(project_id) / f"{asset_id}.png"
                    if alt.is_file():
                        return alt.read_bytes(), content_type
                    raise NotFoundError("That asset file is not available.")
            if not resolved.is_file():
                alt = self._asset_root / str(project_id) / f"{asset_id}.png"
                if alt.is_file():
                    return alt.read_bytes(), content_type
                raise NotFoundError("That asset file is missing on disk.")
            return resolved.read_bytes(), content_type

        # Direct filesystem fallback when BINARY_ASSET row is absent
        path = self._asset_root / str(project_id) / f"{asset_id}.png"
        if path.is_file():
            return path.read_bytes(), "image/png"

        raise NotFoundError("No asset with that id for this game.")

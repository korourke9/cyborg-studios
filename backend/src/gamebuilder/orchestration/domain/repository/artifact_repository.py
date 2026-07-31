from typing import Protocol
from uuid import UUID

from gamebuilder.orchestration.domain.model.artifact import Artifact


class ArtifactRepository(Protocol):
    async def save(self, artifact: Artifact) -> Artifact: ...

    async def find_by_project_id(self, project_id: UUID) -> list[Artifact]: ...

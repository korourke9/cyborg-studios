from dataclasses import dataclass
from uuid import UUID

from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType


@dataclass(frozen=True)
class Artifact:
    id: UUID
    project_id: UUID
    type: ArtifactType
    payload: str
    created_at: int

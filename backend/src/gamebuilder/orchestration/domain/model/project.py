from dataclasses import dataclass
from uuid import UUID

from gamebuilder.orchestration.domain.model.project_status import ProjectStatus


@dataclass(frozen=True)
class Project:
    id: UUID
    prompt: str
    status: ProjectStatus
    created_at: int
    updated_at: int

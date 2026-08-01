from contextlib import AbstractAsyncContextManager
from typing import Protocol

from gamebuilder.orchestration.domain.repository.artifact_repository import ArtifactRepository
from gamebuilder.orchestration.domain.repository.project_repository import ProjectRepository


class UnitOfWork(Protocol):
    """Single database transaction spanning project and artifact writes."""

    projects: ProjectRepository
    artifacts: ArtifactRepository


class UnitOfWorkFactory(Protocol):
    def __call__(self) -> AbstractAsyncContextManager[UnitOfWork]: ...

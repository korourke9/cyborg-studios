from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.infrastructure.persistence.models import ArtifactRow


class SqlAlchemyArtifactRepository:
    """Artifact persistence scoped to a single UnitOfWork session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, artifact: Artifact) -> Artifact:
        self._session.add(
            ArtifactRow(
                id=artifact.id,
                project_id=artifact.project_id,
                type=artifact.type.value,
                payload=artifact.payload,
                created_at=artifact.created_at,
            )
        )
        await self._session.flush()
        return artifact

    async def find_by_project_id(self, project_id: UUID) -> list[Artifact]:
        result = await self._session.execute(
            select(ArtifactRow)
            .where(ArtifactRow.project_id == project_id)
            .order_by(ArtifactRow.created_at.asc())
        )
        rows = result.scalars().all()
        return [
            Artifact(
                id=row.id,
                project_id=row.project_id,
                type=ArtifactType(row.type),
                payload=row.payload,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def delete_by_project_id(self, project_id: UUID) -> None:
        await self._session.execute(
            delete(ArtifactRow).where(ArtifactRow.project_id == project_id)
        )

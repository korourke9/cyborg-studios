from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from gamebuilder.orchestration.domain.model.artifact import Artifact
from gamebuilder.orchestration.domain.model.artifact_type import ArtifactType
from gamebuilder.orchestration.infrastructure.persistence.models import ArtifactRow


class SqlAlchemyArtifactRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, artifact: Artifact) -> Artifact:
        async with self._session_factory() as session:
            session.add(
                ArtifactRow(
                    id=artifact.id,
                    project_id=artifact.project_id,
                    type=artifact.type.value,
                    payload=artifact.payload,
                    created_at=artifact.created_at,
                )
            )
            await session.commit()
        return artifact

    async def find_by_project_id(self, project_id: UUID) -> list[Artifact]:
        async with self._session_factory() as session:
            result = await session.execute(
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

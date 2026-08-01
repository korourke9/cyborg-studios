from time import time
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from gamebuilder.orchestration.domain.model.project import Project
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.orchestration.infrastructure.persistence.models import ProjectRow


class SqlAlchemyProjectRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, project: Project) -> Project:
        async with self._session_factory() as session:
            session.add(
                ProjectRow(
                    id=project.id,
                    prompt=project.prompt,
                    status=project.status.value,
                    created_at=project.created_at,
                    updated_at=project.updated_at,
                )
            )
            await session.commit()
        return project

    async def find_by_id(self, project_id: UUID) -> Project | None:
        async with self._session_factory() as session:
            row = await session.get(ProjectRow, project_id)
            if row is None:
                return None
            return self._to_domain(row)

    async def list_recent(self) -> list[Project]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProjectRow).order_by(ProjectRow.updated_at.desc())
            )
            return [self._to_domain(row) for row in result.scalars().all()]

    async def update_status(self, project_id: UUID, status: ProjectStatus) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(ProjectRow)
                .where(ProjectRow.id == project_id)
                .values(status=status.value, updated_at=int(time() * 1000))
            )
            await session.commit()

    @staticmethod
    def _to_domain(row: ProjectRow) -> Project:
        return Project(
            id=row.id,
            prompt=row.prompt,
            status=ProjectStatus(row.status),
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

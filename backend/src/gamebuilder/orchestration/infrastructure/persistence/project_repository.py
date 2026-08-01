from time import time
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from gamebuilder.orchestration.domain.model.project import Project
from gamebuilder.orchestration.domain.model.project_status import ProjectStatus
from gamebuilder.orchestration.infrastructure.persistence.models import ProjectRow


class SqlAlchemyProjectRepository:
    """Project persistence scoped to a single UnitOfWork session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, project: Project) -> Project:
        self._session.add(
            ProjectRow(
                id=project.id,
                prompt=project.prompt,
                status=project.status.value,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )
        await self._session.flush()
        return project

    async def find_by_id(self, project_id: UUID) -> Project | None:
        row = await self._session.get(ProjectRow, project_id)
        if row is None:
            return None
        return self._to_domain(row)

    async def list_recent(self) -> list[Project]:
        result = await self._session.execute(
            select(ProjectRow).order_by(ProjectRow.updated_at.desc())
        )
        return [self._to_domain(row) for row in result.scalars().all()]

    async def update_status(self, project_id: UUID, status: ProjectStatus) -> None:
        await self._session.execute(
            update(ProjectRow)
            .where(ProjectRow.id == project_id)
            .values(status=status.value, updated_at=int(time() * 1000))
        )

    async def delete(self, project_id: UUID) -> None:
        await self._session.execute(delete(ProjectRow).where(ProjectRow.id == project_id))

    @staticmethod
    def _to_domain(row: ProjectRow) -> Project:
        return Project(
            id=row.id,
            prompt=row.prompt,
            status=ProjectStatus(row.status),
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

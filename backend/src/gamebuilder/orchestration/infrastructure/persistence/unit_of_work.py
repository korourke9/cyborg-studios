from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from gamebuilder.orchestration.application.port.unit_of_work import UnitOfWork
from gamebuilder.orchestration.infrastructure.persistence.artifact_repository import (
    SqlAlchemyArtifactRepository,
)
from gamebuilder.orchestration.infrastructure.persistence.project_repository import (
    SqlAlchemyProjectRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.projects = SqlAlchemyProjectRepository(session)
        self.artifacts = SqlAlchemyArtifactRepository(session)


def create_unit_of_work_factory(
    session_factory: async_sessionmaker[AsyncSession],
):
    @asynccontextmanager
    async def unit_of_work() -> AsyncIterator[UnitOfWork]:
        session = session_factory()
        uow = SqlAlchemyUnitOfWork(session)
        try:
            yield uow
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    return unit_of_work

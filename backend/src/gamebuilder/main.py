import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gamebuilder.orchestration.infrastructure.config.container import (
    AppContainer,
    build_container,
    init_database,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.interfaces.web.exception_handlers import (
    register_exception_handlers,
)
from gamebuilder.orchestration.interfaces.web.routers import router


def _default_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        container: AppContainer = await build_container(settings)
        await init_database(container.engine)
        app.state.container = container

        worker_task: asyncio.Task[None] | None = None
        if container.worker is not None:
            worker_task = asyncio.create_task(container.worker.run())

        try:
            yield
        finally:
            if worker_task is not None:
                worker_task.cancel()
                try:
                    await worker_task
                except asyncio.CancelledError:
                    pass
            await container.engine.dispose()

    return lifespan


def create_app(
    settings: Settings | None = None,
    *,
    lifespan_factory: Callable[[Settings], Callable] | None = None,
) -> FastAPI:
    settings = settings or Settings()
    lifespan = (lifespan_factory or _default_lifespan)(settings)
    app = FastAPI(title="Cyborg Studios Game Builder", lifespan=lifespan)
    register_exception_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()

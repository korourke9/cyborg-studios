from typing import Protocol
from uuid import UUID


class GenerationWorkflowRunner(Protocol):
    async def start(self, project_id: UUID) -> None: ...

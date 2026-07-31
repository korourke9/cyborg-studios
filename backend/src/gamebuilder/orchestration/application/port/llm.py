from enum import StrEnum
from typing import Protocol


class ModelCapability(StrEnum):
    DESIGN = "DESIGN"
    WRITING = "WRITING"
    ART = "ART"
    ENGINEERING = "ENGINEERING"
    QA = "QA"
    PRODUCER = "PRODUCER"


class LlmModel(Protocol):
    def complete(self, *, system: str, user: str) -> str:
        """Single LLM turn: system + user messages → response text."""


class LlmRouter(Protocol):
    def for_capability(self, capability: ModelCapability) -> LlmModel:
        """Resolve the configured model for a studio capability."""

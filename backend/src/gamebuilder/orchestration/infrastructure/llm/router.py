from collections.abc import Callable

from gamebuilder.orchestration.application.port.llm import LlmModel, LlmRouter, ModelCapability


class ConfigLlmRouter:
    def __init__(self, models: dict[ModelCapability, LlmModel]) -> None:
        self._models = models

    def for_capability(self, capability: ModelCapability) -> LlmModel:
        try:
            return self._models[capability]
        except KeyError as exc:
            raise KeyError(f"No LLM configured for capability {capability}") from exc


class ScriptedLlmModel:
    """Test double that returns scripted completions in order."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)

    def complete(self, *, system: str, user: str) -> str:
        if not self._responses:
            raise RuntimeError("ScriptedLlmModel has no remaining responses")
        return self._responses.pop(0)


def build_capability_map(
    factory: Callable[[str], LlmModel],
    *,
    default_model: str,
    overrides: dict[ModelCapability, str] | None = None,
) -> dict[ModelCapability, LlmModel]:
    overrides = overrides or {}
    return {
        capability: factory(overrides.get(capability, default_model))
        for capability in ModelCapability
    }

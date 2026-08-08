from openai import OpenAI

from gamebuilder.orchestration.application.port.llm import LlmModel, LlmRouter, ModelCapability
from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
    model_id_for_capability,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.openai_compatible_model import (
    OpenAICompatibleLlmModel,
)
from gamebuilder.orchestration.infrastructure.llm.router import (
    ConfigLlmRouter,
    build_capability_map,
)

_DEFAULT_BASE_URLS = {
    "ollama": "http://127.0.0.1:11434/v1",
    "lmstudio": "http://127.0.0.1:1234/v1",
}


def create_llm_router(settings: Settings) -> LlmRouter | None:
    """Build an LlmRouter from settings, or None when no live model is configured.

    Cloud vs local is decided only in this adapter layer. Application/team code uses LlmModel.
    """
    if not settings.llm_is_configured():
        return None

    provider = settings.normalized_llm_provider()
    client = _build_client(settings, provider)
    json_mode = _resolve_json_mode(settings, provider)

    def factory(model_id: str) -> LlmModel:
        return OpenAICompatibleLlmModel(client, model_id, json_mode=json_mode)

    overrides = {
        capability: model_id_for_capability(settings, capability)
        for capability in ModelCapability
    }

    return ConfigLlmRouter(
        build_capability_map(
            factory,
            default_model=model_id_for_capability(settings, ModelCapability.DESIGN),
            overrides=overrides,
        )
    )


def _resolve_json_mode(settings: Settings, provider: str) -> bool:
    # Many local servers reject OpenAI response_format=json_object.
    if provider in {"ollama", "lmstudio", "vllm"}:
        return settings.llm_json_mode if settings.llm_json_mode_explicit else False
    return settings.llm_json_mode


def _build_client(settings: Settings, provider: str) -> OpenAI:
    if provider == "openai":
        if not settings.llm_api_key:
            raise ValueError("LLM_PROVIDER=openai requires LLM_API_KEY")
        return OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url or None,
        )

    if provider in {"ollama", "openai_compatible", "vllm", "lmstudio"}:
        base_url = settings.llm_base_url or _DEFAULT_BASE_URLS.get(provider)
        if not base_url:
            raise ValueError(
                f"LLM_PROVIDER={provider} requires LLM_BASE_URL "
                "(OpenAI-compatible root, e.g. http://127.0.0.1:11434/v1)"
            )
        return OpenAI(
            api_key=settings.llm_api_key or "local",
            base_url=base_url,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER={settings.llm_provider!r}; "
        "supported: none, openai, openai_compatible, ollama, vllm, lmstudio. "
        "Add an adapter under orchestration.infrastructure.llm for others."
    )

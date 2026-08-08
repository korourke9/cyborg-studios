"""Build PydanticAI Model instances from transport-agnostic settings."""

from pydantic_ai.models import Model
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
    model_id_for_capability,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings

_DEFAULT_BASE_URLS = {
    "ollama": "http://127.0.0.1:11434/v1",
    "lmstudio": "http://127.0.0.1:1234/v1",
}

# Local OpenAI-compatible servers often ignore schema tools and emit prose;
# json_object forces parseable output for PydanticAI structured agents.
_JSON_OBJECT_PROVIDERS = frozenset(
    {"ollama", "openai_compatible", "vllm", "lmstudio"}
)


def create_pydantic_ai_model_settings(settings: Settings) -> ModelSettings:
    """ModelSettings for structured team agents (JSON mode for local providers)."""
    provider = settings.normalized_llm_provider()
    extra_body: dict | None = None
    if settings.llm_json_mode and provider in _JSON_OBJECT_PROVIDERS:
        extra_body = {"response_format": {"type": "json_object"}}
    return ModelSettings(temperature=0.2, extra_body=extra_body)


def create_pydantic_ai_model(
    settings: Settings,
    capability: ModelCapability,
    *,
    model_id: str | None = None,
) -> Model:
    """Map LLM_* settings to a PydanticAI Model. Used only by infrastructure agent adapters."""
    if not settings.llm_is_configured():
        raise RuntimeError("Cannot create PydanticAI model: LLM is not configured")

    provider = settings.normalized_llm_provider()
    resolved_id = model_id or model_id_for_capability(settings, capability)

    if provider == "openai":
        return OpenAIChatModel(
            resolved_id,
            provider=OpenAIProvider(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url or None,
            ),
        )

    if provider == "ollama":
        base_url = settings.llm_base_url or _DEFAULT_BASE_URLS["ollama"]
        return OllamaModel(
            resolved_id,
            provider=OllamaProvider(
                base_url=base_url,
                api_key=settings.llm_api_key,
            ),
        )

    if provider in {"openai_compatible", "vllm", "lmstudio"}:
        base_url = settings.llm_base_url or _DEFAULT_BASE_URLS.get(provider)
        if not base_url:
            raise ValueError(
                f"LLM_PROVIDER={provider} requires LLM_BASE_URL for PydanticAI"
            )
        return OpenAIChatModel(
            resolved_id,
            provider=OpenAIProvider(
                api_key=settings.llm_api_key or "local",
                base_url=base_url,
            ),
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER={settings.llm_provider!r} for PydanticAI; "
        "supported: openai, ollama, openai_compatible, vllm, lmstudio"
    )

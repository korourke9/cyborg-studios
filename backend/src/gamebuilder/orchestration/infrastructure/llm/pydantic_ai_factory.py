"""Build PydanticAI Model instances from transport-agnostic settings."""

from pydantic_ai.models import Model
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openai import OpenAIProvider

from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.infrastructure.config.settings import Settings

_DEFAULT_BASE_URLS = {
    "ollama": "http://127.0.0.1:11434/v1",
    "lmstudio": "http://127.0.0.1:1234/v1",
}


def model_id_for_capability(settings: Settings, capability: ModelCapability) -> str:
    mapping = {
        ModelCapability.DESIGN: settings.llm_model_design,
        ModelCapability.WRITING: settings.llm_model_writing,
        ModelCapability.ART: settings.llm_model_art,
        ModelCapability.ENGINEERING: settings.llm_model_engineering,
        ModelCapability.QA: settings.llm_model_qa,
        ModelCapability.PRODUCER: settings.llm_model_producer,
    }
    return mapping[capability]


def create_pydantic_ai_model(settings: Settings, capability: ModelCapability) -> Model:
    """Map LLM_* settings to a PydanticAI Model. Used only by infrastructure agent adapters."""
    if not settings.llm_is_configured():
        raise RuntimeError("Cannot create PydanticAI model: LLM is not configured")

    provider = settings.normalized_llm_provider()
    model_id = model_id_for_capability(settings, capability)

    if provider == "openai":
        return OpenAIChatModel(
            model_id,
            provider=OpenAIProvider(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url or None,
            ),
        )

    if provider == "ollama":
        base_url = settings.llm_base_url or _DEFAULT_BASE_URLS["ollama"]
        return OllamaModel(
            model_id,
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
            model_id,
            provider=OpenAIProvider(
                api_key=settings.llm_api_key or "local",
                base_url=base_url,
            ),
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER={settings.llm_provider!r} for PydanticAI; "
        "supported: openai, ollama, openai_compatible, vllm, lmstudio"
    )

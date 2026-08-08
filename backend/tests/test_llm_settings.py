from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
    model_id_for_capability,
    resolve_agent_runtime,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model_settings,
)
from gamebuilder.team.art.application.agent_spec import ART_AGENT_SPEC
from gamebuilder.team.design.application.agent_spec import DESIGN_AGENT_SPEC


def test_llm_not_configured_by_default() -> None:
    assert Settings().llm_is_configured() is False
    assert Settings().resolve_design_agent_mode() == "deterministic"


def test_openai_requires_api_key() -> None:
    assert Settings(llm_provider="openai").llm_is_configured() is False
    assert Settings(llm_provider="openai", llm_api_key="sk-test").llm_is_configured() is True


def test_ollama_configured_without_api_key() -> None:
    settings = Settings(llm_provider="ollama", llm_model_design="llama3.2")
    assert settings.llm_is_configured() is True
    assert settings.resolve_design_agent_mode() == "pydantic_ai"


def test_ollama_model_settings_request_json_object() -> None:
    settings = Settings(llm_provider="ollama", llm_json_mode=True)
    ms = create_pydantic_ai_model_settings(settings)
    assert ms.get("extra_body") == {"response_format": {"type": "json_object"}}


def test_openai_model_settings_skip_forced_json_object() -> None:
    settings = Settings(llm_provider="openai", llm_api_key="sk-test", llm_json_mode=True)
    ms = create_pydantic_ai_model_settings(settings)
    assert ms.get("extra_body") is None


def test_openai_compatible_requires_base_url() -> None:
    assert Settings(llm_provider="openai_compatible").llm_is_configured() is False
    assert Settings(
        llm_provider="openai_compatible",
        llm_base_url="http://127.0.0.1:8000/v1",
    ).llm_is_configured() is True


def test_team_spec_default_model_when_no_override() -> None:
    settings = Settings()
    runtime = resolve_agent_runtime(DESIGN_AGENT_SPEC, settings)
    assert runtime.model_id == DESIGN_AGENT_SPEC.default_model_id
    assert model_id_for_capability(settings, ModelCapability.DESIGN) == "llama3.2"


def test_team_spec_model_override_from_settings() -> None:
    settings = Settings(llm_model_design="qwen2.5")
    runtime = resolve_agent_runtime(DESIGN_AGENT_SPEC, settings)
    assert runtime.model_id == "qwen2.5"


def test_art_spec_declares_image_roles() -> None:
    settings = Settings(image_provider="none")
    runtime = resolve_agent_runtime(ART_AGENT_SPEC, settings)
    assert "hero" in runtime.image_roles
    assert runtime.image_generation_enabled is False


def test_art_image_generation_enabled_when_a1111_configured() -> None:
    settings = Settings(image_provider="automatic1111")
    runtime = resolve_agent_runtime(ART_AGENT_SPEC, settings)
    assert runtime.image_generation_enabled is True

from gamebuilder.orchestration.infrastructure.config.settings import Settings


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


def test_openai_compatible_requires_base_url() -> None:
    assert Settings(llm_provider="openai_compatible").llm_is_configured() is False
    assert Settings(
        llm_provider="openai_compatible",
        llm_base_url="http://127.0.0.1:8000/v1",
    ).llm_is_configured() is True

import os

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql+asyncpg://gamebuilder:gamebuilder@localhost:5432/gamebuilder"
    )
    temporal_target: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_task_queue: str = "game-generation"
    cors_allowed_origins: str = "http://localhost:3000"
    port: int = 8080

    # Transport-agnostic LLM wiring — adapters live only under infrastructure.llm.
    # none/off → no live model (deterministic design in auto mode).
    llm_provider: str = "none"
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    # OpenAI-style response_format=json_object (often unsupported by local servers).
    llm_json_mode: bool = True
    llm_json_mode_explicit: bool = Field(default=False, exclude=True)

    # auto: pydantic_ai when LLM is configured, otherwise deterministic
    design_agent_mode: str = "auto"
    story_agent_mode: str = "auto"
    art_agent_mode: str = "auto"
    engineering_agent_mode: str = "auto"
    qa_agent_mode: str = "auto"
    producer_agent_mode: str = "auto"

    llm_model_design: str = "gpt-4o-mini"
    llm_model_writing: str = "gpt-4o-mini"
    llm_model_art: str = "gpt-4o-mini"
    llm_model_engineering: str = "gpt-4o-mini"
    llm_model_qa: str = "gpt-4o-mini"
    llm_model_producer: str = "gpt-4o-mini"

    @model_validator(mode="after")
    def _note_explicit_json_mode(self) -> "Settings":
        # Local providers default JSON-mode off unless the env var was set.
        object.__setattr__(
            self, "llm_json_mode_explicit", "LLM_JSON_MODE" in os.environ
        )
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]

    def normalized_llm_provider(self) -> str:
        return self.llm_provider.strip().lower()

    def llm_is_configured(self) -> bool:
        """True when settings are sufficient to build an LlmRouter (cloud or local)."""
        provider = self.normalized_llm_provider()
        if not provider or provider in {"none", "off", "disabled"}:
            return False
        if provider == "openai":
            return bool(self.llm_api_key)
        if provider in {"ollama", "lmstudio"}:
            # Base URL optional — factory supplies localhost defaults.
            return True
        if provider in {"openai_compatible", "vllm"}:
            return bool(self.llm_base_url)
        return bool(self.llm_api_key or self.llm_base_url)

    def resolve_design_agent_mode(self) -> str:
        mode = self.design_agent_mode.strip().lower()
        if mode == "auto":
            return "pydantic_ai" if self.llm_is_configured() else "deterministic"
        if mode in {"pydantic_ai", "reflective", "langgraph", "deterministic"}:
            return mode
        raise ValueError(
            f"Invalid DESIGN_AGENT_MODE={self.design_agent_mode!r}; "
            "expected auto, pydantic_ai, reflective, langgraph, or deterministic"
        )

    def resolve_story_agent_mode(self) -> str:
        mode = self.story_agent_mode.strip().lower()
        if mode == "auto":
            return "pydantic_ai" if self.llm_is_configured() else "deterministic"
        if mode in {"pydantic_ai", "deterministic"}:
            return mode
        raise ValueError(
            f"Invalid STORY_AGENT_MODE={self.story_agent_mode!r}; "
            "expected auto, pydantic_ai, or deterministic"
        )

    def resolve_art_agent_mode(self) -> str:
        mode = self.art_agent_mode.strip().lower()
        if mode == "auto":
            return "pydantic_ai" if self.llm_is_configured() else "deterministic"
        if mode in {"pydantic_ai", "deterministic"}:
            return mode
        raise ValueError(
            f"Invalid ART_AGENT_MODE={self.art_agent_mode!r}; "
            "expected auto, pydantic_ai, or deterministic"
        )

    def resolve_engineering_agent_mode(self) -> str:
        mode = self.engineering_agent_mode.strip().lower()
        if mode == "auto":
            return "pydantic_ai" if self.llm_is_configured() else "deterministic"
        if mode in {"pydantic_ai", "deterministic"}:
            return mode
        raise ValueError(
            f"Invalid ENGINEERING_AGENT_MODE={self.engineering_agent_mode!r}; "
            "expected auto, pydantic_ai, or deterministic"
        )

    def resolve_qa_agent_mode(self) -> str:
        mode = self.qa_agent_mode.strip().lower()
        if mode == "auto":
            return "pydantic_ai" if self.llm_is_configured() else "deterministic"
        if mode in {"pydantic_ai", "deterministic"}:
            return mode
        raise ValueError(
            f"Invalid QA_AGENT_MODE={self.qa_agent_mode!r}; "
            "expected auto, pydantic_ai, or deterministic"
        )

    def resolve_producer_agent_mode(self) -> str:
        mode = self.producer_agent_mode.strip().lower()
        if mode == "auto":
            return "pydantic_ai" if self.llm_is_configured() else "deterministic"
        if mode in {"pydantic_ai", "deterministic"}:
            return mode
        raise ValueError(
            f"Invalid PRODUCER_AGENT_MODE={self.producer_agent_mode!r}; "
            "expected auto, pydantic_ai, or deterministic"
        )

import os
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from gamebuilder.orchestration.application.port.llm import ModelCapability


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

    # Browser-reachable API origin for asset URLs embedded in Phaser scripts.
    public_api_base_url: str = "http://localhost:8080"

    # Local asset storage (BINARY_ASSET files).
    asset_storage_dir: str = "data/assets"

    # Transport-agnostic LLM wiring — adapters live only under infrastructure.llm.
    # none/off → no live model (deterministic agents in auto mode).
    # Local-first default for docs/examples is ollama; runtime default stays none
    # so tests and fresh clones stay deterministic until configured.
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

    # Optional env overrides; empty → use TeamAgentSpec.default_model_id
    llm_model_design: str = ""
    llm_model_writing: str = ""
    llm_model_art: str = ""
    llm_model_engineering: str = ""
    llm_model_qa: str = ""
    llm_model_producer: str = ""

    # Image generation (separate from chat). Local-first: automatic1111 / forge.
    image_provider: str = "none"
    image_api_key: str | None = None
    image_base_url: str | None = None
    image_model: str = ""
    image_size: str = "512x512"
    image_soft_fail: bool = True

    # Engineering experiment: also emit SDK JS + security review alongside IR compile.
    engineering_sdk_enabled: bool = True
    engineering_sdk_llm_review: bool = True
    engineering_sdk_llm_authorship: bool = True

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

    def asset_root(self) -> Path:
        return Path(self.asset_storage_dir).expanduser().resolve()

    def normalized_llm_provider(self) -> str:
        return self.llm_provider.strip().lower()

    def normalized_image_provider(self) -> str:
        return self.image_provider.strip().lower()

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

    def image_is_configured(self) -> bool:
        provider = self.normalized_image_provider()
        if not provider or provider in {"none", "off", "disabled"}:
            return False
        if provider in {"automatic1111", "a1111", "forge"}:
            return True  # base URL optional — defaults to host.docker.internal:7860
        if provider == "openai":
            return bool(self.image_api_key or self.llm_api_key)
        return False

    def model_id_override_for(self, capability: ModelCapability) -> str | None:
        mapping = {
            ModelCapability.DESIGN: self.llm_model_design,
            ModelCapability.WRITING: self.llm_model_writing,
            ModelCapability.ART: self.llm_model_art,
            ModelCapability.ENGINEERING: self.llm_model_engineering,
            ModelCapability.QA: self.llm_model_qa,
            ModelCapability.PRODUCER: self.llm_model_producer,
        }
        value = mapping[capability].strip()
        return value or None

    # Thin wrappers kept for call sites / tests — delegate to TeamAgentSpec resolver.
    def resolve_design_agent_mode(self) -> str:
        from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
            resolve_agent_runtime,
        )
        from gamebuilder.team.design.application.agent_spec import DESIGN_AGENT_SPEC

        return resolve_agent_runtime(DESIGN_AGENT_SPEC, self).mode

    def resolve_story_agent_mode(self) -> str:
        from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
            resolve_agent_runtime,
        )
        from gamebuilder.team.story.application.agent_spec import STORY_AGENT_SPEC

        return resolve_agent_runtime(STORY_AGENT_SPEC, self).mode

    def resolve_art_agent_mode(self) -> str:
        from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
            resolve_agent_runtime,
        )
        from gamebuilder.team.art.application.agent_spec import ART_AGENT_SPEC

        return resolve_agent_runtime(ART_AGENT_SPEC, self).mode

    def resolve_engineering_agent_mode(self) -> str:
        from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
            resolve_agent_runtime,
        )
        from gamebuilder.team.engineering.application.agent_spec import (
            ENGINEERING_AGENT_SPEC,
        )

        return resolve_agent_runtime(ENGINEERING_AGENT_SPEC, self).mode

    def resolve_qa_agent_mode(self) -> str:
        from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
            resolve_agent_runtime,
        )
        from gamebuilder.team.qa.application.agent_spec import QA_AGENT_SPEC

        return resolve_agent_runtime(QA_AGENT_SPEC, self).mode

    def resolve_producer_agent_mode(self) -> str:
        from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
            resolve_agent_runtime,
        )
        from gamebuilder.team.producer.application.agent_spec import PRODUCER_AGENT_SPEC

        return resolve_agent_runtime(PRODUCER_AGENT_SPEC, self).mode

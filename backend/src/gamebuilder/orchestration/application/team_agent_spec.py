"""Declarative per-team agent configuration (framework-free)."""

from dataclasses import dataclass, field

from gamebuilder.orchestration.application.port.llm import ModelCapability


@dataclass(frozen=True)
class TeamAgentSpec:
    """What a studio team needs to run — capability, modes, and model defaults.

    Settings remain the env override surface; this is the team's declaration.
    """

    team_id: str
    chat_capability: ModelCapability
    default_agent_mode: str = "auto"
    allowed_agent_modes: tuple[str, ...] = (
        "auto",
        "pydantic_ai",
        "deterministic",
    )
    default_model_id: str = "llama3.2"
    image_roles: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ResolvedAgentRuntime:
    """Result of merging a TeamAgentSpec with Settings overrides."""

    team_id: str
    mode: str
    model_id: str
    chat_capability: ModelCapability
    image_roles: tuple[str, ...]
    image_generation_enabled: bool

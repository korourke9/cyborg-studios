"""Merge TeamAgentSpec with Settings overrides into a concrete runtime."""

from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.application.team_agent_spec import (
    ResolvedAgentRuntime,
    TeamAgentSpec,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings


def resolve_agent_runtime(
    spec: TeamAgentSpec, settings: Settings
) -> ResolvedAgentRuntime:
    mode = _resolve_mode(spec, settings)
    model_id = _resolve_model_id(spec, settings)
    image_enabled = bool(spec.image_roles) and settings.image_is_configured()
    return ResolvedAgentRuntime(
        team_id=spec.team_id,
        mode=mode,
        model_id=model_id,
        chat_capability=spec.chat_capability,
        image_roles=spec.image_roles,
        image_generation_enabled=image_enabled,
    )


def _configured_mode_override(spec: TeamAgentSpec, settings: Settings) -> str:
    mapping = {
        "design": settings.design_agent_mode,
        "story": settings.story_agent_mode,
        "art": settings.art_agent_mode,
        "engineering": settings.engineering_agent_mode,
        "qa": settings.qa_agent_mode,
        "producer": settings.producer_agent_mode,
    }
    return mapping[spec.team_id].strip().lower()


def _resolve_mode(spec: TeamAgentSpec, settings: Settings) -> str:
    raw = _configured_mode_override(spec, settings) or spec.default_agent_mode
    if raw == "auto":
        resolved = "pydantic_ai" if settings.llm_is_configured() else "deterministic"
    else:
        resolved = raw
    if resolved not in spec.allowed_agent_modes and raw != "auto":
        allowed = ", ".join(spec.allowed_agent_modes)
        raise ValueError(
            f"Invalid agent mode {raw!r} for team {spec.team_id!r}; "
            f"expected one of: {allowed}"
        )
    if resolved not in spec.allowed_agent_modes:
        # auto resolved to something not allowed — should not happen if auto is allowed
        raise ValueError(
            f"Resolved mode {resolved!r} is not allowed for team {spec.team_id!r}"
        )
    return resolved


def _resolve_model_id(spec: TeamAgentSpec, settings: Settings) -> str:
    override = settings.model_id_override_for(spec.chat_capability)
    if override:
        return override
    return spec.default_model_id


def all_team_specs() -> tuple[TeamAgentSpec, ...]:
    from gamebuilder.team.art.application.agent_spec import ART_AGENT_SPEC
    from gamebuilder.team.design.application.agent_spec import DESIGN_AGENT_SPEC
    from gamebuilder.team.engineering.application.agent_spec import ENGINEERING_AGENT_SPEC
    from gamebuilder.team.producer.application.agent_spec import PRODUCER_AGENT_SPEC
    from gamebuilder.team.qa.application.agent_spec import QA_AGENT_SPEC
    from gamebuilder.team.story.application.agent_spec import STORY_AGENT_SPEC

    return (
        DESIGN_AGENT_SPEC,
        STORY_AGENT_SPEC,
        ART_AGENT_SPEC,
        ENGINEERING_AGENT_SPEC,
        QA_AGENT_SPEC,
        PRODUCER_AGENT_SPEC,
    )


def model_id_for_capability(
    settings: Settings, capability: ModelCapability
) -> str:
    """Resolve model id for a capability using the matching team spec defaults."""
    for spec in all_team_specs():
        if spec.chat_capability == capability:
            return _resolve_model_id(spec, settings)
    override = settings.model_id_override_for(capability)
    return override or "llama3.2"

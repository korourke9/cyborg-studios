from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
    resolve_agent_runtime,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
    create_pydantic_ai_model_settings,
)
from gamebuilder.team.art.application.agent_spec import ART_AGENT_SPEC
from gamebuilder.team.art.application.port.art_agent_graph import ArtAgentGraph
from gamebuilder.team.art.infrastructure.agent.deterministic_art_agent_graph import (
    DeterministicArtAgentGraph,
)
from gamebuilder.team.art.infrastructure.agent.pydantic_ai_art_agent_graph import (
    PydanticAIArtAgentGraph,
)


def build_art_agent_graph(
    *, mode: str | None = None, settings: Settings
) -> ArtAgentGraph:
    runtime = resolve_agent_runtime(ART_AGENT_SPEC, settings)
    resolved = mode or runtime.mode
    if resolved == "deterministic":
        return DeterministicArtAgentGraph()
    if resolved == "pydantic_ai":
        model = create_pydantic_ai_model(
            settings, runtime.chat_capability, model_id=runtime.model_id
        )
        return PydanticAIArtAgentGraph(
            model,
            model_settings=create_pydantic_ai_model_settings(settings),
        )
    raise ValueError(
        f"Unknown art agent mode {resolved!r}; expected deterministic or pydantic_ai"
    )

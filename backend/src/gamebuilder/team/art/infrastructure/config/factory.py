from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
)
from gamebuilder.team.art.application.port.art_agent_graph import ArtAgentGraph
from gamebuilder.team.art.infrastructure.agent.deterministic_art_agent_graph import (
    DeterministicArtAgentGraph,
)
from gamebuilder.team.art.infrastructure.agent.pydantic_ai_art_agent_graph import (
    PydanticAIArtAgentGraph,
)


def build_art_agent_graph(*, mode: str, settings: Settings) -> ArtAgentGraph:
    if mode == "deterministic":
        return DeterministicArtAgentGraph()

    if mode == "pydantic_ai":
        model = create_pydantic_ai_model(settings, ModelCapability.ART)
        return PydanticAIArtAgentGraph(model)

    raise ValueError(
        f"Unknown art agent mode {mode!r}; expected deterministic or pydantic_ai"
    )

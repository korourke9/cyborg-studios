from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
)
from gamebuilder.team.story.application.port.story_agent_graph import StoryAgentGraph
from gamebuilder.team.story.infrastructure.agent.deterministic_story_agent_graph import (
    DeterministicStoryAgentGraph,
)
from gamebuilder.team.story.infrastructure.agent.pydantic_ai_story_agent_graph import (
    PydanticAIStoryAgentGraph,
)


def build_story_agent_graph(*, mode: str, settings: Settings) -> StoryAgentGraph:
    """Compose the story team's AgentGraph implementation for the requested mode."""
    if mode == "deterministic":
        return DeterministicStoryAgentGraph()

    if mode == "pydantic_ai":
        model = create_pydantic_ai_model(settings, ModelCapability.WRITING)
        return PydanticAIStoryAgentGraph(model)

    raise ValueError(
        f"Unknown story agent mode {mode!r}; expected deterministic or pydantic_ai"
    )

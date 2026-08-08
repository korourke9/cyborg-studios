from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
    resolve_agent_runtime,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
    create_pydantic_ai_model_settings,
)
from gamebuilder.team.story.application.agent_spec import STORY_AGENT_SPEC
from gamebuilder.team.story.application.port.story_agent_graph import StoryAgentGraph
from gamebuilder.team.story.infrastructure.agent.deterministic_story_agent_graph import (
    DeterministicStoryAgentGraph,
)
from gamebuilder.team.story.infrastructure.agent.pydantic_ai_story_agent_graph import (
    PydanticAIStoryAgentGraph,
)


def build_story_agent_graph(
    *, mode: str | None = None, settings: Settings
) -> StoryAgentGraph:
    runtime = resolve_agent_runtime(STORY_AGENT_SPEC, settings)
    resolved = mode or runtime.mode
    if resolved == "deterministic":
        return DeterministicStoryAgentGraph()
    if resolved == "pydantic_ai":
        model = create_pydantic_ai_model(
            settings, runtime.chat_capability, model_id=runtime.model_id
        )
        return PydanticAIStoryAgentGraph(
            model,
            model_settings=create_pydantic_ai_model_settings(settings),
        )
    raise ValueError(
        f"Unknown story agent mode {resolved!r}; expected deterministic or pydantic_ai"
    )

from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
    resolve_agent_runtime,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
    create_pydantic_ai_model_settings,
)
from gamebuilder.team.engineering.application.agent_spec import ENGINEERING_AGENT_SPEC
from gamebuilder.team.engineering.application.port.engineering_agent_graph import (
    EngineeringAgentGraph,
)
from gamebuilder.team.engineering.infrastructure.agent.deterministic_engineering_agent_graph import (
    DeterministicEngineeringAgentGraph,
)
from gamebuilder.team.engineering.infrastructure.agent.pydantic_ai_engineering_agent_graph import (
    PydanticAIEngineeringAgentGraph,
)


def build_engineering_agent_graph(
    *, mode: str | None = None, settings: Settings
) -> EngineeringAgentGraph:
    runtime = resolve_agent_runtime(ENGINEERING_AGENT_SPEC, settings)
    resolved = mode or runtime.mode
    if resolved == "deterministic":
        return DeterministicEngineeringAgentGraph()
    if resolved == "pydantic_ai":
        model = create_pydantic_ai_model(
            settings, runtime.chat_capability, model_id=runtime.model_id
        )
        return PydanticAIEngineeringAgentGraph(
            model,
            model_settings=create_pydantic_ai_model_settings(settings),
        )
    raise ValueError(
        "Unknown engineering agent mode "
        f"{resolved!r}; expected deterministic or pydantic_ai"
    )

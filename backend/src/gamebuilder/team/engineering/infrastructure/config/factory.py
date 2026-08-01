from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
)
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
    *, mode: str, settings: Settings
) -> EngineeringAgentGraph:
    if mode == "deterministic":
        return DeterministicEngineeringAgentGraph()

    if mode == "pydantic_ai":
        model = create_pydantic_ai_model(settings, ModelCapability.ENGINEERING)
        return PydanticAIEngineeringAgentGraph(model)

    raise ValueError(
        "Unknown engineering agent mode "
        f"{mode!r}; expected deterministic or pydantic_ai"
    )

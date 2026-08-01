from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
)
from gamebuilder.team.producer.application.port.producer_agent_graph import (
    ProducerAgentGraph,
)
from gamebuilder.team.producer.infrastructure.agent.deterministic_producer_agent_graph import (
    DeterministicProducerAgentGraph,
)
from gamebuilder.team.producer.infrastructure.agent.pydantic_ai_producer_agent_graph import (
    PydanticAIProducerAgentGraph,
)


def build_producer_agent_graph(
    *, mode: str, settings: Settings
) -> ProducerAgentGraph:
    if mode == "deterministic":
        return DeterministicProducerAgentGraph()

    if mode == "pydantic_ai":
        model = create_pydantic_ai_model(settings, ModelCapability.PRODUCER)
        return PydanticAIProducerAgentGraph(model)

    raise ValueError(
        "Unknown producer agent mode "
        f"{mode!r}; expected deterministic or pydantic_ai"
    )

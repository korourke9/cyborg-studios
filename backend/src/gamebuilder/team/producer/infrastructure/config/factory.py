from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
    resolve_agent_runtime,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
    create_pydantic_ai_model_settings,
)
from gamebuilder.team.producer.application.agent_spec import PRODUCER_AGENT_SPEC
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
    *, mode: str | None = None, settings: Settings
) -> ProducerAgentGraph:
    runtime = resolve_agent_runtime(PRODUCER_AGENT_SPEC, settings)
    resolved = mode or runtime.mode
    if resolved == "deterministic":
        return DeterministicProducerAgentGraph()
    if resolved == "pydantic_ai":
        model = create_pydantic_ai_model(
            settings, runtime.chat_capability, model_id=runtime.model_id
        )
        return PydanticAIProducerAgentGraph(
            model,
            model_settings=create_pydantic_ai_model_settings(settings),
        )
    raise ValueError(
        "Unknown producer agent mode "
        f"{resolved!r}; expected deterministic or pydantic_ai"
    )

from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
)
from gamebuilder.team.qa.application.port.qa_agent_graph import QaAgentGraph
from gamebuilder.team.qa.infrastructure.agent.deterministic_qa_agent_graph import (
    DeterministicQaAgentGraph,
)
from gamebuilder.team.qa.infrastructure.agent.pydantic_ai_qa_agent_graph import (
    PydanticAIQaAgentGraph,
)


def build_qa_agent_graph(*, mode: str, settings: Settings) -> QaAgentGraph:
    if mode == "deterministic":
        return DeterministicQaAgentGraph()

    if mode == "pydantic_ai":
        model = create_pydantic_ai_model(settings, ModelCapability.QA)
        return PydanticAIQaAgentGraph(model)

    raise ValueError(
        f"Unknown qa agent mode {mode!r}; expected deterministic or pydantic_ai"
    )

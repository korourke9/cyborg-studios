from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
    resolve_agent_runtime,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
    create_pydantic_ai_model_settings,
)
from gamebuilder.team.qa.application.agent_spec import QA_AGENT_SPEC
from gamebuilder.team.qa.application.port.qa_agent_graph import QaAgentGraph
from gamebuilder.team.qa.infrastructure.agent.deterministic_qa_agent_graph import (
    DeterministicQaAgentGraph,
)
from gamebuilder.team.qa.infrastructure.agent.pydantic_ai_qa_agent_graph import (
    PydanticAIQaAgentGraph,
)


def build_qa_agent_graph(
    *, mode: str | None = None, settings: Settings
) -> QaAgentGraph:
    runtime = resolve_agent_runtime(QA_AGENT_SPEC, settings)
    resolved = mode or runtime.mode
    if resolved == "deterministic":
        return DeterministicQaAgentGraph()
    if resolved == "pydantic_ai":
        model = create_pydantic_ai_model(
            settings, runtime.chat_capability, model_id=runtime.model_id
        )
        return PydanticAIQaAgentGraph(
            model,
            model_settings=create_pydantic_ai_model_settings(settings),
        )
    raise ValueError(
        f"Unknown qa agent mode {resolved!r}; expected deterministic or pydantic_ai"
    )

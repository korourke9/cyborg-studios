from gamebuilder.orchestration.application.port.llm import LlmRouter
from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
    resolve_agent_runtime,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.llm.factory import create_llm_router
from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_factory import (
    create_pydantic_ai_model,
    create_pydantic_ai_model_settings,
)
from gamebuilder.team.design.application.agent_spec import DESIGN_AGENT_SPEC
from gamebuilder.team.design.application.port.design_agent_graph import DesignAgentGraph
from gamebuilder.team.design.application.reflective_design_agent_graph import (
    ReflectiveDesignAgentGraph,
)
from gamebuilder.team.design.infrastructure.agent.deterministic_design_agent_graph import (
    DeterministicDesignAgentGraph,
)
from gamebuilder.team.design.infrastructure.agent.langgraph_design_agent_graph import (
    LangGraphDesignAgentGraph,
)
from gamebuilder.team.design.infrastructure.agent.pydantic_ai_design_agent_graph import (
    PydanticAIDesignAgentGraph,
)


def build_design_agent_graph(
    *,
    mode: str | None = None,
    settings: Settings,
    llm_router: LlmRouter | None = None,
) -> DesignAgentGraph:
    """Compose the design team's AgentGraph implementation for the requested mode."""
    runtime = resolve_agent_runtime(DESIGN_AGENT_SPEC, settings)
    resolved = mode or runtime.mode

    if resolved == "deterministic":
        return DeterministicDesignAgentGraph()

    if resolved == "pydantic_ai":
        model = create_pydantic_ai_model(
            settings,
            runtime.chat_capability,
            model_id=runtime.model_id,
        )
        return PydanticAIDesignAgentGraph(
            model,
            model_settings=create_pydantic_ai_model_settings(settings),
        )

    router = llm_router if llm_router is not None else create_llm_router(settings)
    if router is None:
        raise RuntimeError(
            f"DESIGN_AGENT_MODE={resolved} requires a configured LLM "
            "(set LLM_PROVIDER and provider settings, or use DESIGN_AGENT_MODE=deterministic)"
        )

    if resolved == "reflective":
        return ReflectiveDesignAgentGraph(router)
    if resolved == "langgraph":
        return LangGraphDesignAgentGraph(router)

    raise ValueError(
        f"Unknown design agent mode {resolved!r}; "
        "expected deterministic, pydantic_ai, reflective, or langgraph"
    )

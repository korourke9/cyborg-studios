from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from gamebuilder.orchestration.application.port.llm import LlmRouter, ModelCapability
from gamebuilder.team.design.application.design_reflection import DesignReflectionProcess
from gamebuilder.team.design.domain.model import DesignTeamInput, DesignTeamOutput


class DesignGraphState(TypedDict, total=False):
    prompt: str
    draft_json: str
    critique_json: str
    revised_json: str
    validated_output: DesignTeamOutput | None
    validation_error: str | None


class LangGraphDesignAgentGraph:
    """Thin LangGraph adapter over DesignReflectionProcess (same steps, graph runtime)."""

    def __init__(self, llm_router: LlmRouter) -> None:
        llm = llm_router.for_capability(ModelCapability.DESIGN)
        self._process = DesignReflectionProcess(llm)
        self._graph = self._build_graph()

    def run(self, input: DesignTeamInput) -> DesignTeamOutput:
        result = self._graph.invoke({"prompt": input.prompt})
        output = result.get("validated_output")
        if output is None:
            error = result.get("validation_error") or "Design graph produced no output"
            raise RuntimeError(error)
        return output

    def _build_graph(self) -> Any:
        graph: StateGraph = StateGraph(DesignGraphState)
        graph.add_node("draft", self._draft)
        graph.add_node("critique", self._critique)
        graph.add_node("revise", self._revise)
        graph.add_node("validate", self._validate)
        graph.set_entry_point("draft")
        graph.add_edge("draft", "critique")
        graph.add_edge("critique", "revise")
        graph.add_edge("revise", "validate")
        graph.add_edge("validate", END)
        return graph.compile()

    def _draft(self, state: DesignGraphState) -> DesignGraphState:
        return {**state, "draft_json": self._process.draft(state["prompt"])}

    def _critique(self, state: DesignGraphState) -> DesignGraphState:
        return {
            **state,
            "critique_json": self._process.critique(state["prompt"], state["draft_json"]),
        }

    def _revise(self, state: DesignGraphState) -> DesignGraphState:
        return {
            **state,
            "revised_json": self._process.revise(
                state["prompt"], state["draft_json"], state["critique_json"]
            ),
        }

    def _validate(self, state: DesignGraphState) -> DesignGraphState:
        candidate = state.get("revised_json") or state.get("draft_json") or ""
        try:
            output = self._process.validate(candidate, allow_repair=True)
            return {**state, "validated_output": output, "validation_error": None}
        except Exception as exc:  # noqa: BLE001 - surface as graph error state
            return {**state, "validated_output": None, "validation_error": str(exc)}

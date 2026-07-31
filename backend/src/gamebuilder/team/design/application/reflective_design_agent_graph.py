from gamebuilder.orchestration.application.port.llm import LlmRouter, ModelCapability
from gamebuilder.team.design.application.design_reflection import DesignReflectionProcess
from gamebuilder.team.design.domain.model import DesignTeamInput, DesignTeamOutput


class ReflectiveDesignAgentGraph:
    """DesignAgentGraph implementation: linear reflection over LlmModel (no agent framework)."""

    def __init__(self, llm_router: LlmRouter) -> None:
        llm = llm_router.for_capability(ModelCapability.DESIGN)
        self._process = DesignReflectionProcess(llm)

    def run(self, input: DesignTeamInput) -> DesignTeamOutput:
        return self._process.run(input.prompt)

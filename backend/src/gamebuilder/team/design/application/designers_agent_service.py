from gamebuilder.team.design.application.port.design_agent_graph import DesignAgentGraph
from gamebuilder.team.design.domain.model import DesignTeamInput, DesignTeamOutput


class DesignersAgentService:
    def __init__(self, design_agent_graph: DesignAgentGraph) -> None:
        self._design_agent_graph = design_agent_graph

    def generate_initial_design(self, prompt: str) -> DesignTeamOutput:
        return self._design_agent_graph.run(DesignTeamInput(prompt=prompt))

from gamebuilder.team.engineering.application.port.engineering_agent_graph import (
    EngineeringAgentGraph,
)
from gamebuilder.team.engineering.domain.model import (
    EngineeringTeamInput,
    EngineeringTeamOutput,
)


class EngineersAgentService:
    def __init__(self, engineering_agent_graph: EngineeringAgentGraph) -> None:
        self._engineering_agent_graph = engineering_agent_graph

    def generate_bundle(self, input: EngineeringTeamInput) -> EngineeringTeamOutput:
        return self._engineering_agent_graph.run(input)

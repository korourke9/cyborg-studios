from gamebuilder.team.producer.application.port.producer_agent_graph import (
    ProducerAgentGraph,
)
from gamebuilder.team.producer.domain.model import ProducerTeamInput, ProducerTeamOutput


class ProducerAgentService:
    def __init__(self, producer_agent_graph: ProducerAgentGraph) -> None:
        self._producer_agent_graph = producer_agent_graph

    def review(self, input: ProducerTeamInput) -> ProducerTeamOutput:
        return self._producer_agent_graph.run(input)

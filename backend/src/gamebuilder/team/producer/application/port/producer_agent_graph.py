from typing import Protocol

from gamebuilder.team.producer.domain.model import ProducerTeamInput, ProducerTeamOutput


class ProducerAgentGraph(Protocol):
    def run(self, input: ProducerTeamInput) -> ProducerTeamOutput: ...

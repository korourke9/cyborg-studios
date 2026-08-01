from typing import Protocol

from gamebuilder.team.engineering.domain.model import (
    EngineeringTeamInput,
    EngineeringTeamOutput,
)


class EngineeringAgentGraph(Protocol):
    def run(self, input: EngineeringTeamInput) -> EngineeringTeamOutput: ...

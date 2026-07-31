from typing import Protocol

from gamebuilder.team.design.domain.model import DesignTeamInput, DesignTeamOutput


class DesignAgentGraph(Protocol):
    def run(self, input: DesignTeamInput) -> DesignTeamOutput: ...

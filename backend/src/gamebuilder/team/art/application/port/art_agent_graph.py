from typing import Protocol

from gamebuilder.team.art.domain.model import ArtTeamInput, ArtTeamOutput


class ArtAgentGraph(Protocol):
    def run(self, input: ArtTeamInput) -> ArtTeamOutput: ...

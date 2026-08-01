from gamebuilder.team.art.application.port.art_agent_graph import ArtAgentGraph
from gamebuilder.team.art.domain.model import ArtTeamInput, ArtTeamOutput


class ArtTeamAgentService:
    def __init__(self, art_agent_graph: ArtAgentGraph) -> None:
        self._art_agent_graph = art_agent_graph

    def generate_art(self, input: ArtTeamInput) -> ArtTeamOutput:
        return self._art_agent_graph.run(input)

from gamebuilder.team.qa.application.port.qa_agent_graph import QaAgentGraph
from gamebuilder.team.qa.domain.model import QaTeamInput, QaTeamOutput


class QaAgentService:
    def __init__(self, qa_agent_graph: QaAgentGraph) -> None:
        self._qa_agent_graph = qa_agent_graph

    def review(self, input: QaTeamInput) -> QaTeamOutput:
        return self._qa_agent_graph.run(input)

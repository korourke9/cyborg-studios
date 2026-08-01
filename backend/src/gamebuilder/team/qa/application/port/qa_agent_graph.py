from typing import Protocol

from gamebuilder.team.qa.domain.model import QaTeamInput, QaTeamOutput


class QaAgentGraph(Protocol):
    def run(self, input: QaTeamInput) -> QaTeamOutput: ...

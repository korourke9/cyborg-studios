from typing import Protocol

from gamebuilder.team.story.domain.model import StoryTeamInput, StoryTeamOutput


class StoryAgentGraph(Protocol):
    def run(self, input: StoryTeamInput) -> StoryTeamOutput: ...

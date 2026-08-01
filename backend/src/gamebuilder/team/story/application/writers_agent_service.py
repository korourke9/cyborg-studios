from gamebuilder.team.story.application.port.story_agent_graph import StoryAgentGraph
from gamebuilder.team.story.domain.model import StoryTeamInput, StoryTeamOutput


class WritersAgentService:
    def __init__(self, story_agent_graph: StoryAgentGraph) -> None:
        self._story_agent_graph = story_agent_graph

    def generate_story(self, input: StoryTeamInput) -> StoryTeamOutput:
        return self._story_agent_graph.run(input)

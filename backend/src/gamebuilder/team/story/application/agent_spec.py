from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.application.team_agent_spec import TeamAgentSpec

STORY_AGENT_SPEC = TeamAgentSpec(
    team_id="story",
    chat_capability=ModelCapability.WRITING,
    default_model_id="llama3.2",
)

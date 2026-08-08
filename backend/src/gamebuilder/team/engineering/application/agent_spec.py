from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.application.team_agent_spec import TeamAgentSpec

ENGINEERING_AGENT_SPEC = TeamAgentSpec(
    team_id="engineering",
    chat_capability=ModelCapability.ENGINEERING,
    default_model_id="llama3.2",
)

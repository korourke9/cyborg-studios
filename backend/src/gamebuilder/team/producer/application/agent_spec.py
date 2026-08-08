from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.application.team_agent_spec import TeamAgentSpec

PRODUCER_AGENT_SPEC = TeamAgentSpec(
    team_id="producer",
    chat_capability=ModelCapability.PRODUCER,
    default_model_id="llama3.2",
)

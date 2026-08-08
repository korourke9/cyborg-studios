from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.application.team_agent_spec import TeamAgentSpec

QA_AGENT_SPEC = TeamAgentSpec(
    team_id="qa",
    chat_capability=ModelCapability.QA,
    default_model_id="llama3.2",
)

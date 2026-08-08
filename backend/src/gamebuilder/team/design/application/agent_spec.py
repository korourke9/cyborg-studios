from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.application.team_agent_spec import TeamAgentSpec

DESIGN_AGENT_SPEC = TeamAgentSpec(
    team_id="design",
    chat_capability=ModelCapability.DESIGN,
    allowed_agent_modes=(
        "auto",
        "pydantic_ai",
        "reflective",
        "langgraph",
        "deterministic",
    ),
    default_model_id="llama3.2",
)

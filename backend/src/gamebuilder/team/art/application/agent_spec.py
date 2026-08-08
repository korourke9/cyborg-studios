from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.application.team_agent_spec import TeamAgentSpec

ART_AGENT_SPEC = TeamAgentSpec(
    team_id="art",
    chat_capability=ModelCapability.ART,
    default_model_id="llama3.2",
    image_roles=(
        "hero",
        "key-level-backdrop",
        "signature-hazard",
        "key-level-tiles",
        "collectible",
    ),
)

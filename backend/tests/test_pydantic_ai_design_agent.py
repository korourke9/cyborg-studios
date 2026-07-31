from pydantic_ai.models.test import TestModel

from gamebuilder.team.design.domain.model import DesignTeamInput
from gamebuilder.team.design.infrastructure.agent.pydantic_ai_design_agent_graph import (
    PydanticAIDesignAgentGraph,
)

VALID_DESIGN = {
    "visionDoc": {
        "summary": "A glowing cave platformer about a tiny robot.",
        "playerFantasy": "Dash through crystal tunnels with confident jumps.",
        "targetMood": "Curious and kinetic.",
    },
    "designPillars": {
        "pillars": [
            "Readable movement before complexity",
            "One memorable crystal-dash twist",
            "Short levels with fast restarts",
        ]
    },
    "mechanicsSpec": {
        "movement": "Run, jump, and short air-dash.",
        "coreLoop": "Explore, dash through hazards, collect shards, reach the exit.",
        "verbs": ["run", "jump", "dash", "collect", "finish"],
    },
    "systemsSpec": {
        "progression": "Teach jump, then dash in a safe room.",
        "challenge": "Gaps and spikes escalate while checkpoints stay close.",
        "scoring": "Reward speed, shards, and no-hit clears.",
    },
}

CRITIQUE = {
    "issues": [],
    "severity": [],
    "suggestions": ["Keep the dash readable in dark rooms."],
}


def test_pydantic_ai_design_agent_with_test_models() -> None:
    graph = PydanticAIDesignAgentGraph(
        TestModel(custom_output_args=VALID_DESIGN),
        critique_model=TestModel(custom_output_args=CRITIQUE),
        revise_model=TestModel(custom_output_args=VALID_DESIGN),
    )
    output = graph.run(DesignTeamInput(prompt="A tiny robot adventure in a glowing cave"))
    assert "robot" in output.vision_doc.summary.lower() or "cave" in output.vision_doc.summary.lower()
    assert len(output.design_pillars.pillars) == 3
    assert "jump" in output.mechanics_spec.verbs

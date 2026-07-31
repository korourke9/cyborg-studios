import json

from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.orchestration.infrastructure.llm.router import (
    ConfigLlmRouter,
    ScriptedLlmModel,
)
from gamebuilder.team.design.domain.model import DesignTeamInput
from gamebuilder.team.design.application.reflective_design_agent_graph import (
    ReflectiveDesignAgentGraph,
)
from gamebuilder.team.design.infrastructure.agent.langgraph_design_agent_graph import (
    LangGraphDesignAgentGraph,
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


def _scripted_router() -> ConfigLlmRouter:
    draft = json.dumps(VALID_DESIGN)
    critique = json.dumps(CRITIQUE)
    revise = json.dumps(VALID_DESIGN)
    return ConfigLlmRouter(
        {ModelCapability.DESIGN: ScriptedLlmModel([draft, critique, revise])}
    )


def test_reflective_design_agent_with_scripted_llm() -> None:
    graph = ReflectiveDesignAgentGraph(_scripted_router())
    output = graph.run(DesignTeamInput(prompt="A tiny robot adventure in a glowing cave"))
    assert len(output.design_pillars.pillars) == 3
    assert "jump" in output.mechanics_spec.verbs
    assert output.systems_spec.scoring


def test_langgraph_adapter_uses_same_reflection_process() -> None:
    graph = LangGraphDesignAgentGraph(_scripted_router())
    output = graph.run(DesignTeamInput(prompt="A tiny robot adventure in a glowing cave"))
    assert "robot" in output.vision_doc.summary.lower() or "cave" in output.vision_doc.summary.lower()
    assert len(output.design_pillars.pillars) == 3

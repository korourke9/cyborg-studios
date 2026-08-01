from gamebuilder.team.story.domain.model import StoryTeamInput
from gamebuilder.team.story.infrastructure.agent.deterministic_story_agent_graph import (
    DeterministicStoryAgentGraph,
)


def test_deterministic_story_agent_produces_narrative_and_beats() -> None:
    output = DeterministicStoryAgentGraph().run(
        StoryTeamInput(
            prompt="A tiny robot adventure in a glowing cave",
            vision_summary="A focused 2D platformer in a glowing cave.",
            design_pillars=(
                "Readable movement before complexity",
                "One memorable twist from the prompt",
                "Short levels with fast restarts",
            ),
            player_fantasy="Dash through crystal tunnels",
        )
    )
    assert "robot" in output.narrative_spec.premise.lower() or "cave" in output.narrative_spec.premise.lower()
    assert output.narrative_spec.protagonist
    assert len(output.experience_milestones.milestones) >= 3

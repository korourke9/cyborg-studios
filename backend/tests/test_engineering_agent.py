from gamebuilder.team.engineering.domain.model import EngineeringTeamInput
from gamebuilder.team.engineering.infrastructure.agent.deterministic_engineering_agent_graph import (
    DeterministicEngineeringAgentGraph,
)


def test_deterministic_engineering_agent_produces_playable_bundle() -> None:
    output = DeterministicEngineeringAgentGraph().run(
        EngineeringTeamInput(
            prompt="A tiny robot adventure in a glowing cave",
            vision_summary="A focused 2D platformer in a glowing cave.",
            core_loop="Jump across platforms to the glow",
            narrative_tone="Warm and lightly heroic",
            setting="Crystal tunnels",
            art_style="Readable soft pixel shapes",
            background_hex="#fff4e8",
            player_hex="#9b7ed9",
            platform_hex="#3a2a4a",
            goal_hex="#ff8c42",
        )
    )
    bundle = output.game_bundle
    assert bundle.engine == "phaser3"
    assert len(bundle.platforms) >= 2
    assert bundle.goal.w > 0
    assert "Phaser.Game" in bundle.entry_source
    assert "game-root" in bundle.entry_source
    assert bundle.player_hex == "#9b7ed9"

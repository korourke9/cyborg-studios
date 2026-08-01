from gamebuilder.team.art.domain.model import ArtTeamInput
from gamebuilder.team.art.infrastructure.agent.deterministic_art_agent_graph import (
    DeterministicArtAgentGraph,
)


def test_deterministic_art_agent_produces_direction_and_assets() -> None:
    output = DeterministicArtAgentGraph().run(
        ArtTeamInput(
            prompt="A tiny robot adventure in a glowing cave",
            vision_summary="A focused 2D platformer in a glowing cave.",
            target_mood="Curious and kinetic",
            narrative_tone="Warm and lightly heroic",
            setting="Crystal tunnels",
        )
    )
    assert output.art_direction.hero_concept
    assert output.art_direction.palette[0].role == "primary"
    assert output.art_direction.palette[0].hex.startswith("#")
    assert len(output.art_direction.key_scenes) >= 2
    assert any(asset.role == "hero" for asset in output.asset_list.assets)
    assert len(output.asset_prompts.prompts) >= 3

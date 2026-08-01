from gamebuilder.team.art.domain.model import (
    ArtDirection,
    ArtTeamInput,
    ArtTeamOutput,
    AssetList,
    AssetListItem,
    AssetPromptItem,
    AssetPrompts,
    PaletteColor,
)


class DeterministicArtAgentGraph:
    def run(self, input: ArtTeamInput) -> ArtTeamOutput:
        mood = input.target_mood or input.narrative_tone or "playful"
        prompt = input.prompt.strip() or "the player's adventure"
        setting = input.setting or "compact glowing stages"
        return ArtTeamOutput(
            art_direction=ArtDirection(
                style=(
                    "Readable 2D shapes with soft pixel edges and clear silhouettes, "
                    f"built around “{prompt}”."
                ),
                palette=[
                    PaletteColor(role="primary", hex="#9b7ed9"),
                    PaletteColor(role="secondary", hex="#ff8c42"),
                    PaletteColor(role="accent", hex="#3de7ff"),
                    PaletteColor(role="background", hex="#fff4e8"),
                    PaletteColor(role="ink", hex="#3a2a4a"),
                ],
                mood=mood,
                hero_concept=(
                    f"A small, friendly lead character for “{prompt}”: oversized boots "
                    "or chassis for readable landings, one signature glow accent, "
                    "and a pose that sells the player fantasy."
                ),
                world_concept=(
                    f"Key levels live in {setting}: layered midgrounds, warm light "
                    "pools for safe ground, cooler haze in the distance, and props "
                    "that telegraph jumps before the player commits."
                ),
                key_scenes=[
                    f"First reveal of the world inspired by “{prompt}”.",
                    "A safe room that teaches the signature visual twist.",
                    "A denser hazard stretch where palette contrast does the teaching.",
                    "A short finale overlook that rewards collecting and clean movement.",
                ],
                notes=(
                    "No final bitmaps yet — these briefs stand in for concept art. "
                    "Asset prompts below are ready for later image generation."
                ),
            ),
            asset_list=AssetList(
                assets=[
                    AssetListItem(id="player", role="hero", file_ref="placeholder://hero"),
                    AssetListItem(
                        id="tiles", role="key-level-tiles", file_ref="placeholder://tiles"
                    ),
                    AssetListItem(
                        id="hazard", role="signature-hazard", file_ref="placeholder://hazard"
                    ),
                    AssetListItem(
                        id="collectible",
                        role="collectible",
                        file_ref="placeholder://collectible",
                    ),
                    AssetListItem(
                        id="background",
                        role="key-level-backdrop",
                        file_ref="placeholder://background",
                    ),
                ]
            ),
            asset_prompts=AssetPrompts(
                prompts=[
                    AssetPromptItem(
                        asset_id="player",
                        role="hero",
                        prompt=(
                            f"Concept sheet for the main character in “{prompt}”: "
                            "front/side poses, glow accent, readable silhouette"
                        ),
                    ),
                    AssetPromptItem(
                        asset_id="tiles",
                        role="key-level-tiles",
                        prompt=f"Platform tiles and ledges for {setting}",
                    ),
                    AssetPromptItem(
                        asset_id="hazard",
                        role="signature-hazard",
                        prompt="Signature hazard prop with instant readability",
                    ),
                    AssetPromptItem(
                        asset_id="collectible",
                        role="collectible",
                        prompt="Bright collectible that pops on the palette",
                    ),
                    AssetPromptItem(
                        asset_id="background",
                        role="key-level-backdrop",
                        prompt=f"Key level backdrop for mood “{mood}” in {setting}",
                    ),
                ]
            ),
        )

from gamebuilder.team.engineering.application.phaser_entry import with_compiled_entry
from gamebuilder.team.engineering.domain.model import (
    CollectibleSpec,
    EngineeringTeamInput,
    EngineeringTeamOutput,
    GameBundle,
    HazardSpec,
    PlatformSpec,
)


class DeterministicEngineeringAgentGraph:
    def run(self, input: EngineeringTeamInput) -> EngineeringTeamOutput:
        prompt = input.prompt.strip() or "Untitled run"
        title = prompt if len(prompt) <= 40 else prompt[:37] + "…"
        bundle = GameBundle(
            title=title,
            summary=(
                f"A short readable platforming slice for “{prompt}” "
                f"({input.setting or 'compact stages'}) with hazards and gems."
            ),
            controls="Arrow keys or WASD to move, Space / Up to jump",
            background_hex=input.background_hex or "#1a1424",
            player_hex=input.player_hex or "#9b7ed9",
            platform_hex=input.platform_hex or "#3a2a4a",
            goal_hex=input.goal_hex or "#ff8c42",
            player_start_x=80,
            player_start_y=340,
            world_width=1400,
            world_height=450,
            physics_profile="snappy",
            platforms=[
                PlatformSpec(x=400, y=420, w=800, h=40),
                PlatformSpec(x=220, y=340, w=120, h=16),
                PlatformSpec(x=420, y=280, w=120, h=16),
                PlatformSpec(x=650, y=240, w=140, h=16),
                PlatformSpec(x=900, y=300, w=160, h=16),
                PlatformSpec(x=1150, y=220, w=180, h=16),
                PlatformSpec(x=1100, y=420, w=600, h=40),
            ],
            hazards=[
                HazardSpec(x=340, y=390, w=40, h=20),
                HazardSpec(x=780, y=390, w=48, h=24),
            ],
            collectibles=[
                CollectibleSpec(x=420, y=240, w=18, h=18),
                CollectibleSpec(x=900, y=260, w=18, h=18),
                CollectibleSpec(x=1150, y=180, w=18, h=18),
            ],
            goal=PlatformSpec(x=1280, y=180, w=36, h=36),
            implemented=[
                "run",
                "jump",
                "solid platforms",
                "damaging hazards",
                "collectibles",
                "camera follow",
                "goal overlap win",
            ],
            notes=(
                f"Deterministic IR platformer. Core loop hint: "
                f"{input.core_loop or 'collect gems and reach the goal'}."
            ),
            hero_texture_url=input.hero_texture_url,
            backdrop_texture_url=input.backdrop_texture_url,
            hazard_texture_url=input.hazard_texture_url,
            platform_texture_url=input.platform_texture_url,
            collectible_texture_url=input.collectible_texture_url,
            hero_display_w=input.hero_display_w,
            hero_display_h=input.hero_display_h,
            hazard_display_w=input.hazard_display_w,
            hazard_display_h=input.hazard_display_h,
            collectible_display_w=input.collectible_display_w,
            collectible_display_h=input.collectible_display_h,
            entry_source="",
        )
        return EngineeringTeamOutput(game_bundle=with_compiled_entry(bundle))

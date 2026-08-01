from gamebuilder.team.engineering.application.phaser_entry import with_compiled_entry
from gamebuilder.team.engineering.domain.model import (
    EngineeringTeamInput,
    EngineeringTeamOutput,
    GameBundle,
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
                f"({input.setting or 'compact stages'})."
            ),
            controls="Arrow keys or WASD to move, Space / Up to jump",
            background_hex=input.background_hex or "#fff4e8",
            player_hex=input.player_hex or "#9b7ed9",
            platform_hex=input.platform_hex or "#3a2a4a",
            goal_hex=input.goal_hex or "#ff8c42",
            player_start_x=80,
            player_start_y=340,
            platforms=[
                PlatformSpec(x=400, y=420, w=800, h=40),
                PlatformSpec(x=220, y=340, w=120, h=16),
                PlatformSpec(x=400, y=280, w=120, h=16),
                PlatformSpec(x=580, y=220, w=140, h=16),
            ],
            goal=PlatformSpec(x=700, y=180, w=36, h=36),
            implemented=[
                "run",
                "jump",
                "solid platforms",
                "goal overlap win",
            ],
            notes=(
                f"Deterministic MVP Phaser bundle. Core loop hint: "
                f"{input.core_loop or 'reach the goal'}."
            ),
            entry_source="",
        )
        return EngineeringTeamOutput(game_bundle=with_compiled_entry(bundle))

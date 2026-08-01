from pydantic import BaseModel, Field

from gamebuilder.team.engineering.application.phaser_entry import with_compiled_entry
from gamebuilder.team.engineering.domain.model import (
    EngineeringTeamInput,
    EngineeringTeamOutput,
    GameBundle,
    PlatformSpec,
)

DRAFT_SYSTEM_PROMPT = (
    "You are the Engineering team for a 2D platformer game studio. "
    "Produce a compact Phaser-ready level: title, short summary, controls copy, "
    "player start, a few solid platforms, and a goal rectangle. "
    "Use integer coordinates in an 800x450 world; y grows downward. "
    "Keep the first jump teachable. Do not write JavaScript — only structured level data. "
    "Reuse the provided palette hex colors."
)

CRITIQUE_SYSTEM_PROMPT = (
    "You critique 2D platformer level drafts. Check reachability from start to goal, "
    "jump spacing, and whether platforms leave a readable path. "
    "Flag impossible gaps or starts that fall forever."
)

REVISE_SYSTEM_PROMPT = (
    "You revise a 2D platformer level draft using critique feedback. "
    "Preserve strengths, fix reachability, keep an 800x450 coordinate space."
)


def draft_user_prompt(input: EngineeringTeamInput) -> str:
    return (
        f"Game prompt: {input.prompt}\n"
        f"Vision summary: {input.vision_summary}\n"
        f"Core loop: {input.core_loop}\n"
        f"Narrative tone: {input.narrative_tone}\n"
        f"Setting: {input.setting}\n"
        f"Art style: {input.art_style}\n"
        f"Palette hex — background: {input.background_hex}, "
        f"player: {input.player_hex}, platform: {input.platform_hex}, "
        f"goal: {input.goal_hex}"
    )


def critique_user_prompt(input: EngineeringTeamInput, draft_json: str) -> str:
    return (
        "Critique this engineering level draft.\n"
        f"{draft_user_prompt(input)}\n"
        f"Draft JSON:\n{draft_json}"
    )


def revise_user_prompt(
    input: EngineeringTeamInput, draft_json: str, critique_json: str
) -> str:
    return (
        "Revise this level using the critique.\n"
        f"{draft_user_prompt(input)}\n"
        f"Draft JSON:\n{draft_json}\n"
        f"Critique JSON:\n{critique_json}"
    )


class EngineeringLevelDraft(BaseModel):
    """LLM-facing level shape — entrySource is compiled after finalize."""

    title: str
    engine: str = "phaser3"
    summary: str
    controls: str = "Arrow keys or WASD to move, Space / Up to jump"
    background_hex: str = Field(alias="backgroundHex")
    player_hex: str = Field(alias="playerHex")
    platform_hex: str = Field(alias="platformHex")
    goal_hex: str = Field(alias="goalHex")
    player_start_x: int = Field(alias="playerStartX")
    player_start_y: int = Field(alias="playerStartY")
    platforms: list[PlatformSpec] = Field(min_length=1)
    goal: PlatformSpec
    implemented: list[str] = Field(default_factory=list)
    notes: str = ""

    model_config = {"populate_by_name": True}

    def to_output(self) -> EngineeringTeamOutput:
        bundle = GameBundle(
            title=self.title,
            engine=self.engine,
            summary=self.summary,
            controls=self.controls,
            background_hex=self.background_hex,
            player_hex=self.player_hex,
            platform_hex=self.platform_hex,
            goal_hex=self.goal_hex,
            player_start_x=self.player_start_x,
            player_start_y=self.player_start_y,
            platforms=self.platforms,
            goal=self.goal,
            implemented=self.implemented,
            notes=self.notes,
            entry_source="",
        )
        return EngineeringTeamOutput(game_bundle=with_compiled_entry(bundle))


class CritiqueResult(BaseModel):
    issues: list[str] = Field(default_factory=list)
    severity: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

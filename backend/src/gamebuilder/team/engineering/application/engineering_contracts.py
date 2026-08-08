from pydantic import BaseModel, Field

from gamebuilder.team.engineering.application.phaser_entry import with_compiled_entry
from gamebuilder.team.engineering.domain.model import (
    CollectibleSpec,
    EngineeringTeamInput,
    EngineeringTeamOutput,
    GameBundle,
    HazardSpec,
    PlatformSpec,
)

DRAFT_SYSTEM_PROMPT = (
    "You are the Engineering team for a 2D platformer game studio. "
    "Produce a compact Phaser-ready level as structured JSON only: title, summary, "
    "controls, player start, solid platforms, optional damaging hazards, optional "
    "collectible gems, and a goal rectangle. "
    "Coordinates: integer, y grows downward. Prefer worldWidth 1000–1600 and "
    "worldHeight 450 so the camera can scroll. "
    "physicsProfile must be one of: snappy, floaty, heavy. "
    "Keep the first jump teachable. Place at least one hazard the player can avoid. "
    "Do not write JavaScript — only structured level data. "
    "Reuse the provided palette hex colors. "
    "Respond with a single JSON object only matching the schema. "
    "No markdown, no prose, no code fences."
)

CRITIQUE_SYSTEM_PROMPT = (
    "You critique 2D platformer level drafts. Check reachability from start to goal, "
    "jump spacing, hazard fairness, and whether collectibles are optional or required "
    "without soft-locking. Flag impossible gaps or starts that fall forever. "
    "Respond with a single JSON object only: "
    '{"issues":[string],"severity":[string],"suggestions":[string]}. '
    "No markdown or prose."
)

REVISE_SYSTEM_PROMPT = (
    "You revise a 2D platformer level draft using critique feedback. "
    "Preserve strengths, fix reachability, keep hazards avoidable, "
    "keep physicsProfile in {snappy, floaty, heavy}. "
    "Respond with a single JSON object only matching the schema. "
    "No markdown, no prose, no code fences."
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
    """LLM-facing level shape — entrySource / sdkSource added after finalize."""

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
    hazards: list[HazardSpec] = Field(default_factory=list)
    collectibles: list[CollectibleSpec] = Field(default_factory=list)
    world_width: int = Field(alias="worldWidth", default=1200)
    world_height: int = Field(alias="worldHeight", default=450)
    physics_profile: str = Field(alias="physicsProfile", default="snappy")
    implemented: list[str] = Field(default_factory=list)
    notes: str = ""

    model_config = {"populate_by_name": True}

    def to_output(self) -> EngineeringTeamOutput:
        profile = self.physics_profile if self.physics_profile in {
            "snappy", "floaty", "heavy"
        } else "snappy"
        implemented = list(self.implemented)
        for tag in ("run", "jump", "solid platforms", "goal overlap win"):
            if tag not in implemented:
                implemented.append(tag)
        if self.hazards and "damaging hazards" not in implemented:
            implemented.append("damaging hazards")
        if self.collectibles and "collectibles" not in implemented:
            implemented.append("collectibles")
        if self.world_width > 800 and "camera follow" not in implemented:
            implemented.append("camera follow")

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
            hazards=self.hazards,
            collectibles=self.collectibles,
            world_width=max(800, self.world_width),
            world_height=max(450, self.world_height),
            physics_profile=profile,
            implemented=implemented,
            notes=self.notes,
            entry_source="",
        )
        return EngineeringTeamOutput(game_bundle=with_compiled_entry(bundle))


class CritiqueResult(BaseModel):
    issues: list[str] = Field(default_factory=list)
    severity: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

from dataclasses import dataclass

from pydantic import BaseModel, Field


class PlatformSpec(BaseModel):
    x: int
    y: int
    w: int
    h: int = 16


class GameBundle(BaseModel):
    """Playable MVP bundle: structured level + compiled Phaser entry source."""

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
    entry_source: str = Field(alias="entrySource")

    model_config = {"populate_by_name": True}


@dataclass(frozen=True)
class EngineeringTeamInput:
    prompt: str
    vision_summary: str
    core_loop: str
    narrative_tone: str
    setting: str
    art_style: str
    background_hex: str
    player_hex: str
    platform_hex: str
    goal_hex: str


@dataclass(frozen=True)
class EngineeringTeamOutput:
    game_bundle: GameBundle

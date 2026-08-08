from dataclasses import dataclass

from pydantic import BaseModel, Field


class PlatformSpec(BaseModel):
    x: int
    y: int
    w: int
    h: int = 16


class HazardSpec(BaseModel):
    """Damaging zone — touching restarts the player at spawn."""

    x: int
    y: int
    w: int = 32
    h: int = 32


class CollectibleSpec(BaseModel):
    x: int
    y: int
    w: int = 20
    h: int = 20


class GameBundle(BaseModel):
    """Playable bundle: structured level IR + trusted IR compile + optional SDK JS."""

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
    world_width: int = Field(alias="worldWidth", default=800)
    world_height: int = Field(alias="worldHeight", default=450)
    physics_profile: str = Field(alias="physicsProfile", default="snappy")
    implemented: list[str] = Field(default_factory=list)
    notes: str = ""
    hero_texture_url: str = Field(alias="heroTextureUrl", default="")
    backdrop_texture_url: str = Field(alias="backdropTextureUrl", default="")
    hazard_texture_url: str = Field(alias="hazardTextureUrl", default="")
    platform_texture_url: str = Field(alias="platformTextureUrl", default="")
    collectible_texture_url: str = Field(alias="collectibleTextureUrl", default="")
    hero_display_w: int = Field(alias="heroDisplayW", default=28)
    hero_display_h: int = Field(alias="heroDisplayH", default=32)
    hazard_display_w: int = Field(alias="hazardDisplayW", default=32)
    hazard_display_h: int = Field(alias="hazardDisplayH", default=32)
    collectible_display_w: int = Field(alias="collectibleDisplayW", default=20)
    collectible_display_h: int = Field(alias="collectibleDisplayH", default=20)
    # Trusted compiler output (always present after finalize).
    entry_source: str = Field(alias="entrySource")
    # Optional LLM/SDK experiment path.
    sdk_source: str = Field(alias="sdkSource", default="")
    sdk_review_verdict: str = Field(
        alias="sdkReviewVerdict", default="pending"
    )  # pending | allow | deny | skipped
    sdk_review_notes: list[str] = Field(alias="sdkReviewNotes", default_factory=list)
    # none | template | llm | llm_fallback
    sdk_authorship: str = Field(alias="sdkAuthorship", default="none")
    sdk_gameplay_notes: list[str] = Field(
        alias="sdkGameplayNotes", default_factory=list
    )

    model_config = {"populate_by_name": True}

    def playable_runtimes(self) -> list[str]:
        runtimes = ["ir"]
        if self.sdk_source.strip() and self.sdk_review_verdict == "allow":
            runtimes.append("sdk")
        return runtimes


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
    hero_texture_url: str = ""
    backdrop_texture_url: str = ""
    hazard_texture_url: str = ""
    platform_texture_url: str = ""
    collectible_texture_url: str = ""
    hero_display_w: int = 28
    hero_display_h: int = 32
    hazard_display_w: int = 32
    hazard_display_h: int = 32
    collectible_display_w: int = 20
    collectible_display_h: int = 20


@dataclass(frozen=True)
class EngineeringTeamOutput:
    game_bundle: GameBundle

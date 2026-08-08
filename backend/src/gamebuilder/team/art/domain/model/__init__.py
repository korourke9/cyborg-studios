from dataclasses import dataclass

from pydantic import BaseModel, Field


class PaletteColor(BaseModel):
    role: str
    hex: str


class ArtDirection(BaseModel):
    """Visual concept brief — stand-in for concept art until BINARY_ASSET generation."""

    style: str = "Readable 2D shapes with clear silhouettes"
    palette: list[PaletteColor] = Field(min_length=1)
    mood: str = "playful"
    hero_concept: str = Field(
        alias="heroConcept",
        default="A small, friendly lead character with a readable silhouette",
    )
    world_concept: str = Field(
        alias="worldConcept",
        default="Compact stages with clear safe ground and readable hazards",
    )
    key_scenes: list[str] = Field(
        alias="keyScenes",
        min_length=1,
        default_factory=lambda: [
            "First world reveal",
            "Safe room teaching the visual twist",
            "Hazard stretch using palette contrast",
        ],
    )
    notes: str = ""

    model_config = {"populate_by_name": True}


class AssetListItem(BaseModel):
    id: str
    role: str
    file_ref: str = Field(alias="fileRef", default="placeholder")
    # Filled after sprite prep so Engineering can size Phaser display objects.
    frame_w: int | None = Field(alias="frameW", default=None)
    frame_h: int | None = Field(alias="frameH", default=None)
    processed: bool = False

    model_config = {"populate_by_name": True}


class AssetList(BaseModel):
    assets: list[AssetListItem] = Field(min_length=1)


class AssetPromptItem(BaseModel):
    asset_id: str = Field(alias="assetId")
    role: str
    prompt: str

    model_config = {"populate_by_name": True}


class AssetPrompts(BaseModel):
    prompts: list[AssetPromptItem] = Field(min_length=1)


@dataclass(frozen=True)
class ArtTeamInput:
    prompt: str
    vision_summary: str
    target_mood: str
    narrative_tone: str
    setting: str


@dataclass(frozen=True)
class ArtTeamOutput:
    art_direction: ArtDirection
    asset_list: AssetList
    asset_prompts: AssetPrompts

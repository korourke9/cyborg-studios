from dataclasses import dataclass

from pydantic import BaseModel, Field


class PaletteColor(BaseModel):
    role: str
    hex: str


class ArtDirection(BaseModel):
    """Visual concept brief — stand-in for concept art until BINARY_ASSET generation."""

    style: str
    palette: list[PaletteColor] = Field(min_length=1)
    mood: str
    hero_concept: str = Field(alias="heroConcept")
    world_concept: str = Field(alias="worldConcept")
    key_scenes: list[str] = Field(alias="keyScenes", min_length=1)
    notes: str = ""

    model_config = {"populate_by_name": True}


class AssetListItem(BaseModel):
    id: str
    role: str
    file_ref: str = Field(alias="fileRef", default="placeholder")

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

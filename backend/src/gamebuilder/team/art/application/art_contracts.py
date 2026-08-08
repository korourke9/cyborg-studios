from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from gamebuilder.team.art.domain.model import (
    ArtDirection,
    ArtTeamInput,
    ArtTeamOutput,
    AssetList,
    AssetPrompts,
)

_JSON_ONLY = (
    "Respond with a single JSON object only matching the schema. "
    "No markdown, no prose, no code fences."
)

ART_JSON_SCHEMA = """
Required top-level keys (camelCase): artDirection, assetList, assetPrompts.
Each assetPrompts.prompt must describe a VIDEO GAME asset for a 2D Phaser
platformer (sprite/tile/prop), not a movie still or book illustration.
{
  "artDirection": {
    "style": string,
    "palette": [{"role": "primary"|"secondary"|"accent"|"background"|"ink", "hex": "#RRGGBB"}, ...],
    "mood": string,
    "heroConcept": string,
    "worldConcept": string,
    "keyScenes": [string, ...],
    "notes": string
  },
  "assetList": {
    "assets": [
      {"id": "player", "role": "hero", "fileRef": "placeholder://hero"},
      {"id": "tiles", "role": "key-level-tiles", "fileRef": "placeholder://tiles"},
      {"id": "hazard", "role": "signature-hazard", "fileRef": "placeholder://hazard"},
      {"id": "collectible", "role": "collectible", "fileRef": "placeholder://collectible"},
      {"id": "background", "role": "key-level-backdrop", "fileRef": "placeholder://background"}
    ]
  },
  "assetPrompts": {
    "prompts": [
      {"assetId": "player", "role": "hero", "prompt": "side-view player sprite: …"},
      {"assetId": "tiles", "role": "key-level-tiles", "prompt": "walkable platform tiles: …"},
      {"assetId": "hazard", "role": "signature-hazard", "prompt": "single hazard prop: …"},
      {"assetId": "collectible", "role": "collectible", "prompt": "small pickup sprite: …"},
      {"assetId": "background", "role": "key-level-backdrop", "prompt": "wide stage backdrop: …"}
    ]
  }
}
""".strip()

DRAFT_SYSTEM_PROMPT = (
    "You are the Art team for a 2D platformer game studio. "
    "Produce a visual concept brief: style, a named palette "
    "(primary, secondary, accent, background, ink — each with a hex color), "
    "mood, hero concept, world/level look, and a few key scenes players "
    "should remember. Also output a small asset list with placeholder file "
    "refs and a generation prompt per asset. "
    "Ground the palette in the game vision/setting/mood (e.g. a glowing cave "
    "should use deep ink, cool cyan/teal glow accents, warm stone — not random "
    "neon fashion colors). "
    "Asset prompts must describe in-game sprites/tiles/props for Phaser "
    "(side-view platformer), not cinematic concept art. "
    f"{_JSON_ONLY}\n{ART_JSON_SCHEMA}"
)

CRITIQUE_SYSTEM_PROMPT = (
    "You critique 2D platformer art drafts. Check hero/world clarity, "
    "palette coherence, memorable key scenes, and whether assets cover "
    "player, tiles, hazards, and backdrop needs. "
    "Respond with a single JSON object only: "
    '{"issues":[string],"severity":[string],"suggestions":[string]}. '
    "No markdown or prose."
)

REVISE_SYSTEM_PROMPT = (
    "You revise a 2D platformer art draft using critique feedback. "
    "Preserve strengths and address issues. Keep fileRef values as "
    "placeholders unless a real path is provided. "
    f"{_JSON_ONLY}\n{ART_JSON_SCHEMA}"
)

_DEFAULT_ASSET_DEFS = (
    (
        "player",
        "hero",
        "placeholder://hero",
        "Side-view player character sprite: full body, readable silhouette, "
        "plain background, ready for a Phaser platformer",
    ),
    (
        "tiles",
        "key-level-tiles",
        "placeholder://tiles",
        "Walkable platform and ground tiles matching the world materials",
    ),
    (
        "hazard",
        "signature-hazard",
        "placeholder://hazard",
        "Single hazard prop/tile the player must avoid, clear danger shape",
    ),
    (
        "collectible",
        "collectible",
        "placeholder://collectible",
        "Small shiny collectible pickup sprite that pops on the palette",
    ),
    (
        "background",
        "key-level-backdrop",
        "placeholder://background",
        "Wide level backdrop with empty lower foreground for platforms",
    ),
)


def draft_user_prompt(input: ArtTeamInput) -> str:
    return (
        f"Game prompt: {input.prompt}\n"
        f"Vision summary: {input.vision_summary}\n"
        f"Target mood: {input.target_mood}\n"
        f"Narrative tone: {input.narrative_tone}\n"
        f"Setting: {input.setting}"
    )


def critique_user_prompt(input: ArtTeamInput, draft_json: str) -> str:
    return (
        "Critique this art draft.\n"
        f"{draft_user_prompt(input)}\n"
        f"Draft JSON:\n{draft_json}"
    )


def revise_user_prompt(
    input: ArtTeamInput, draft_json: str, critique_json: str
) -> str:
    return (
        "Revise this art using the critique.\n"
        f"{draft_user_prompt(input)}\n"
        f"Draft JSON:\n{draft_json}\n"
        f"Critique JSON:\n{critique_json}"
    )


def _default_asset_list() -> dict[str, Any]:
    return {
        "assets": [
            {"id": asset_id, "role": role, "fileRef": file_ref}
            for asset_id, role, file_ref, _ in _DEFAULT_ASSET_DEFS
        ]
    }


def _default_asset_prompts(art_direction: dict[str, Any] | None) -> dict[str, Any]:
    hero = ""
    world = ""
    mood = ""
    if isinstance(art_direction, dict):
        hero = str(
            art_direction.get("heroConcept")
            or art_direction.get("hero_concept")
            or ""
        )
        world = str(
            art_direction.get("worldConcept")
            or art_direction.get("world_concept")
            or ""
        )
        mood = str(art_direction.get("mood") or "")

    prompts: list[dict[str, str]] = []
    for asset_id, role, _, base_prompt in _DEFAULT_ASSET_DEFS:
        detail = base_prompt
        if role == "hero" and hero:
            detail = hero
        elif role == "key-level-backdrop" and (world or mood):
            detail = f"{world or base_prompt}. Mood: {mood}".strip()
        prompts.append({"assetId": asset_id, "role": role, "prompt": detail})
    return {"prompts": prompts}


def _section_missing_or_empty(data: dict[str, Any], camel: str, snake: str) -> bool:
    value = data.get(camel, data.get(snake))
    if value is None:
        return True
    if isinstance(value, dict):
        # assetList.assets / assetPrompts.prompts
        nested = value.get("assets")
        if nested is None:
            nested = value.get("prompts")
        if isinstance(nested, list) and len(nested) == 0:
            return True
    return False


class ArtArtifactBundle(BaseModel):
    art_direction: ArtDirection = Field(alias="artDirection")
    asset_list: AssetList = Field(alias="assetList")
    asset_prompts: AssetPrompts = Field(alias="assetPrompts")

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def fill_missing_asset_sections(cls, data: Any) -> Any:
        """Local models often return artDirection only; synthesize asset sections."""
        if not isinstance(data, dict):
            return data
        direction = data.get("artDirection", data.get("art_direction"))
        if _section_missing_or_empty(data, "assetList", "asset_list"):
            data["assetList"] = _default_asset_list()
        if _section_missing_or_empty(data, "assetPrompts", "asset_prompts"):
            data["assetPrompts"] = _default_asset_prompts(
                direction if isinstance(direction, dict) else None
            )
        return data

    def to_output(self) -> ArtTeamOutput:
        return ArtTeamOutput(
            art_direction=self.art_direction,
            asset_list=self.asset_list,
            asset_prompts=self.asset_prompts,
        )


class CritiqueResult(BaseModel):
    issues: list[str] = Field(default_factory=list)
    severity: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

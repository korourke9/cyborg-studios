from pydantic import BaseModel, Field

from gamebuilder.team.art.domain.model import (
    ArtDirection,
    ArtTeamInput,
    ArtTeamOutput,
    AssetList,
    AssetPrompts,
)

DRAFT_SYSTEM_PROMPT = (
    "You are the Art team for a 2D platformer game studio. "
    "Produce a visual concept brief: style, a named palette "
    "(primary, secondary, accent, background, ink — each with a hex color), "
    "mood, hero concept, world/level look, and a few key scenes players "
    "should remember. Also output a small asset list with placeholder file "
    "refs and a generation prompt per asset. Keep platforming readable."
)

CRITIQUE_SYSTEM_PROMPT = (
    "You critique 2D platformer art drafts. Check hero/world clarity, "
    "palette coherence, memorable key scenes, and whether assets cover "
    "player, tiles, hazards, and backdrop needs."
)

REVISE_SYSTEM_PROMPT = (
    "You revise a 2D platformer art draft using critique feedback. "
    "Preserve strengths and address issues. Keep fileRef values as "
    "placeholders unless a real path is provided."
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


class ArtArtifactBundle(BaseModel):
    art_direction: ArtDirection = Field(alias="artDirection")
    asset_list: AssetList = Field(alias="assetList")
    asset_prompts: AssetPrompts = Field(alias="assetPrompts")

    model_config = {"populate_by_name": True}

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

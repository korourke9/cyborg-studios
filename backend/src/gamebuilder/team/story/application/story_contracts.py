from pydantic import BaseModel, Field

from gamebuilder.team.story.domain.model import (
    ExperienceMilestones,
    NarrativeSpec,
    StoryTeamInput,
    StoryTeamOutput,
)

DRAFT_SYSTEM_PROMPT = (
    "You are the Story team for a 2D platformer game studio. "
    "Write a compact narrative that supports readable platforming: "
    "clear premise, memorable protagonist, and short player-experience "
    "milestones that fit level-sized goals. Stay aligned with the design "
    "vision and pillars. "
    "Respond with a single JSON object only matching the schema. "
    "No markdown, no prose, no code fences."
)

CRITIQUE_SYSTEM_PROMPT = (
    "You critique 2D platformer story drafts. Check alignment with the "
    "design vision and pillars, clarity of premise, and whether experience "
    "milestones are short, playable objectives the player can feel. "
    "Respond with a single JSON object only: "
    '{"issues":[string],"severity":[string],"suggestions":[string]}. '
    "No markdown or prose."
)

REVISE_SYSTEM_PROMPT = (
    "You revise a 2D platformer story draft using critique feedback. "
    "Preserve strengths and address issues. "
    "Respond with a single JSON object only matching the schema. "
    "No markdown, no prose, no code fences."
)


def draft_user_prompt(input: StoryTeamInput) -> str:
    pillars = ", ".join(input.design_pillars) if input.design_pillars else "(none)"
    return (
        f"Game prompt: {input.prompt}\n"
        f"Vision summary: {input.vision_summary}\n"
        f"Player fantasy: {input.player_fantasy}\n"
        f"Design pillars: {pillars}"
    )


def critique_user_prompt(input: StoryTeamInput, draft_json: str) -> str:
    return (
        "Critique this story draft.\n"
        f"{draft_user_prompt(input)}\n"
        f"Draft JSON:\n{draft_json}"
    )


def revise_user_prompt(
    input: StoryTeamInput, draft_json: str, critique_json: str
) -> str:
    return (
        "Revise this story using the critique.\n"
        f"{draft_user_prompt(input)}\n"
        f"Draft JSON:\n{draft_json}\n"
        f"Critique JSON:\n{critique_json}"
    )


class StoryArtifactBundle(BaseModel):
    narrative_spec: NarrativeSpec = Field(alias="narrativeSpec")
    experience_milestones: ExperienceMilestones = Field(alias="experienceMilestones")

    model_config = {"populate_by_name": True}

    def to_output(self) -> StoryTeamOutput:
        return StoryTeamOutput(
            narrative_spec=self.narrative_spec,
            experience_milestones=self.experience_milestones,
        )


class CritiqueResult(BaseModel):
    issues: list[str] = Field(default_factory=list)
    severity: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

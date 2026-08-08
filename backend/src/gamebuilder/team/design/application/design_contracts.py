from pydantic import BaseModel, Field

from gamebuilder.team.design.domain.model import (
    DesignPillars,
    DesignTeamOutput,
    MechanicsSpec,
    SystemsSpec,
    VisionDoc,
)

DRAFT_SYSTEM_PROMPT = (
    "You are the Design team for a 2D platformer game studio. "
    "Produce a focused initial design from the user prompt. "
    "Emphasize readable movement, one memorable twist from the prompt, "
    "and short levels with fast restarts. "
    "Respond with a single JSON object only (camelCase keys matching the "
    "schema). No markdown, no prose, no code fences."
)

CRITIQUE_SYSTEM_PROMPT = (
    "You critique 2D platformer design drafts. Check alignment with "
    "readable movement, one memorable prompt twist, and short levels "
    "with fast restarts. "
    "Respond with a single JSON object only: "
    '{"issues":[string],"severity":[string],"suggestions":[string]}. '
    "No markdown or prose."
)

REVISE_SYSTEM_PROMPT = (
    "You revise a 2D platformer design draft using critique feedback. "
    "Preserve strengths and address issues. "
    "Respond with a single JSON object only (camelCase keys matching the "
    "schema). No markdown, no prose, no code fences."
)


def draft_user_prompt(game_prompt: str) -> str:
    return f"Game prompt: {game_prompt}"


def critique_user_prompt(game_prompt: str, draft_json: str) -> str:
    return (
        "Critique this design draft.\n"
        f"Original prompt: {game_prompt}\n"
        f"Draft JSON:\n{draft_json}"
    )


def revise_user_prompt(game_prompt: str, draft_json: str, critique_json: str) -> str:
    return (
        "Revise this design using the critique.\n"
        f"Original prompt: {game_prompt}\n"
        f"Draft JSON:\n{draft_json}\n"
        f"Critique JSON:\n{critique_json}"
    )


class DesignArtifactBundle(BaseModel):
    """Structured design-team output contract (shared by agents and parsers)."""

    vision_doc: VisionDoc = Field(alias="visionDoc")
    design_pillars: DesignPillars = Field(alias="designPillars")
    mechanics_spec: MechanicsSpec = Field(alias="mechanicsSpec")
    systems_spec: SystemsSpec = Field(alias="systemsSpec")

    model_config = {"populate_by_name": True}

    def to_output(self) -> DesignTeamOutput:
        return DesignTeamOutput(
            vision_doc=self.vision_doc,
            design_pillars=self.design_pillars,
            mechanics_spec=self.mechanics_spec,
            systems_spec=self.systems_spec,
        )


class CritiqueResult(BaseModel):
    issues: list[str] = Field(default_factory=list)
    severity: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

from dataclasses import dataclass

from pydantic import BaseModel, Field


class NarrativeSpec(BaseModel):
    premise: str
    tone: str
    protagonist: str
    setting: str


class ExperienceMilestones(BaseModel):
    """Ordered player-experience milestones from first session through early mastery."""

    milestones: list[str] = Field(min_length=1)


@dataclass(frozen=True)
class StoryTeamInput:
    prompt: str
    vision_summary: str
    design_pillars: tuple[str, ...]
    player_fantasy: str


@dataclass(frozen=True)
class StoryTeamOutput:
    narrative_spec: NarrativeSpec
    experience_milestones: ExperienceMilestones

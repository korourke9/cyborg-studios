from dataclasses import dataclass

from pydantic import BaseModel, Field


class VisionDoc(BaseModel):
    summary: str
    player_fantasy: str = Field(alias="playerFantasy")
    target_mood: str = Field(alias="targetMood")

    model_config = {"populate_by_name": True}


class DesignPillars(BaseModel):
    pillars: list[str]


class MechanicsSpec(BaseModel):
    movement: str
    core_loop: str = Field(alias="coreLoop")
    verbs: list[str]

    model_config = {"populate_by_name": True}


class SystemsSpec(BaseModel):
    progression: str
    challenge: str
    scoring: str


@dataclass(frozen=True)
class DesignTeamInput:
    prompt: str


@dataclass(frozen=True)
class DesignTeamOutput:
    vision_doc: VisionDoc
    design_pillars: DesignPillars
    mechanics_spec: MechanicsSpec
    systems_spec: SystemsSpec

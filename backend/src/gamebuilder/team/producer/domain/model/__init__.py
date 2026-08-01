from dataclasses import dataclass

from pydantic import BaseModel, Field


class CoherenceReview(BaseModel):
    """Cross-team coherence judgment before a ship call."""

    aligned: bool
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    summary: str


class ProducerNotes(BaseModel):
    """Ship / revise / cut recommendation for the project."""

    decision: str  # ship | revise | cut
    rationale: str
    cuts: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(alias="nextActions", default_factory=list)
    celebrate: str = ""

    model_config = {"populate_by_name": True}


@dataclass(frozen=True)
class ProducerTeamInput:
    prompt: str
    vision_summary: str
    design_pillars: tuple[str, ...]
    core_loop: str
    narrative_tone: str
    setting: str
    art_mood: str
    bundle_title: str
    bundle_summary: str
    qa_verdict: str
    qa_summary: str
    qa_issue_count: int


@dataclass(frozen=True)
class ProducerTeamOutput:
    coherence_review: CoherenceReview
    producer_notes: ProducerNotes

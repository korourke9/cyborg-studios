from pydantic import BaseModel, Field

from gamebuilder.team.producer.domain.model import (
    CoherenceReview,
    ProducerNotes,
    ProducerTeamInput,
    ProducerTeamOutput,
)

DRAFT_SYSTEM_PROMPT = (
    "You are the Producer for a 2D platformer game studio. "
    "Judge cross-team coherence (vision, story, art, playable build, QA) and "
    "make a ship call: decision must be ship, revise, or cut. "
    "Prefer ship when QA verdict is pass and the build exists; revise when "
    "gaps are fixable; cut only when the concept is incoherent. "
    "Keep notes short and actionable."
)

CRITIQUE_SYSTEM_PROMPT = (
    "You critique a producer coherence review and ship call. "
    "Check that decision matches QA severity and that gaps are concrete."
)

REVISE_SYSTEM_PROMPT = (
    "You revise producer outputs using critique feedback. "
    "Keep decision in {ship, revise, cut} and stay concise."
)


def draft_user_prompt(input: ProducerTeamInput) -> str:
    pillars = "; ".join(input.design_pillars) or "(none)"
    return (
        f"Game prompt: {input.prompt}\n"
        f"Vision: {input.vision_summary}\n"
        f"Pillars: {pillars}\n"
        f"Core loop: {input.core_loop}\n"
        f"Narrative tone: {input.narrative_tone}\n"
        f"Setting: {input.setting}\n"
        f"Art mood: {input.art_mood}\n"
        f"Bundle: {input.bundle_title} — {input.bundle_summary}\n"
        f"QA verdict: {input.qa_verdict}\n"
        f"QA summary: {input.qa_summary}\n"
        f"QA issue count: {input.qa_issue_count}"
    )


def critique_user_prompt(input: ProducerTeamInput, draft_json: str) -> str:
    return (
        "Critique this producer package.\n"
        f"{draft_user_prompt(input)}\n"
        f"Draft JSON:\n{draft_json}"
    )


def revise_user_prompt(
    input: ProducerTeamInput, draft_json: str, critique_json: str
) -> str:
    return (
        "Revise this producer package using the critique.\n"
        f"{draft_user_prompt(input)}\n"
        f"Draft JSON:\n{draft_json}\n"
        f"Critique JSON:\n{critique_json}"
    )


class ProducerArtifactBundle(BaseModel):
    coherence_review: CoherenceReview = Field(alias="coherenceReview")
    producer_notes: ProducerNotes = Field(alias="producerNotes")

    model_config = {"populate_by_name": True}

    def to_output(self) -> ProducerTeamOutput:
        return ProducerTeamOutput(
            coherence_review=self.coherence_review,
            producer_notes=self.producer_notes,
        )


class CritiqueResult(BaseModel):
    issues: list[str] = Field(default_factory=list)
    severity: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

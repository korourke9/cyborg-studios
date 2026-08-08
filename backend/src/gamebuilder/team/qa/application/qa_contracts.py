from pydantic import BaseModel, Field

from gamebuilder.team.qa.domain.model import QaIssue, QaIssues, QaTeamInput, QaTeamOutput

DRAFT_SYSTEM_PROMPT = (
    "You are the QA team for a 2D platformer game studio. "
    "Review the playable level against the vision, core loop, and experience "
    "milestones. Report concrete issues with severity "
    "(blocker, major, minor, note), a short repro, and suggestedFixTeam "
    "(engineering, design, art, story). "
    "Set verdict to pass when there are no blocker/major issues; otherwise "
    "needs_work. Do not invent missing binaries — placeholder art is expected. "
    "Respond with a single JSON object only matching the schema. "
    "No markdown, no prose, no code fences."
)

CRITIQUE_SYSTEM_PROMPT = (
    "You critique a QA report for completeness and fairness. "
    "Ensure blockers are truly unplayable, and that pass/needs_work matches "
    "the issue severities. "
    "Respond with a single JSON object only: "
    '{"issues":[string],"severity":[string],"suggestions":[string]}. '
    "No markdown or prose."
)

REVISE_SYSTEM_PROMPT = (
    "You revise a QA report using critique feedback. Keep checks concrete "
    "and severities calibrated. "
    "Respond with a single JSON object only matching the schema. "
    "No markdown, no prose, no code fences."
)


def draft_user_prompt(input: QaTeamInput) -> str:
    milestones = "; ".join(input.experience_milestones) or "(none)"
    implemented = ", ".join(input.bundle_implemented) or "(none)"
    return (
        f"Game prompt: {input.prompt}\n"
        f"Vision summary: {input.vision_summary}\n"
        f"Core loop: {input.core_loop}\n"
        f"Experience milestones: {milestones}\n"
        f"Bundle title: {input.bundle_title}\n"
        f"Bundle summary: {input.bundle_summary}\n"
        f"Implemented: {implemented}\n"
        f"Platform count: {input.platform_count}\n"
        f"Has entrySource: {input.has_entry_source}\n"
        f"Player start: {input.player_start}\n"
        f"Goal rect (x,y,w,h): {input.goal}"
    )


def critique_user_prompt(input: QaTeamInput, draft_json: str) -> str:
    return (
        "Critique this QA report.\n"
        f"{draft_user_prompt(input)}\n"
        f"Draft JSON:\n{draft_json}"
    )


def revise_user_prompt(
    input: QaTeamInput, draft_json: str, critique_json: str
) -> str:
    return (
        "Revise this QA report using the critique.\n"
        f"{draft_user_prompt(input)}\n"
        f"Draft JSON:\n{draft_json}\n"
        f"Critique JSON:\n{critique_json}"
    )


class QaArtifactBundle(BaseModel):
    qa_issues: QaIssues = Field(alias="qaIssues")

    model_config = {"populate_by_name": True}

    def to_output(self) -> QaTeamOutput:
        return QaTeamOutput(qa_issues=self.qa_issues)


class CritiqueResult(BaseModel):
    issues: list[str] = Field(default_factory=list)
    severity: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

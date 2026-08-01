from dataclasses import dataclass

from pydantic import BaseModel, Field


class QaIssue(BaseModel):
    title: str
    severity: str  # blocker | major | minor | note
    description: str
    repro: str = ""
    suggested_fix_team: str = Field(
        alias="suggestedFixTeam",
        default="engineering",
    )

    model_config = {"populate_by_name": True}


class QaIssues(BaseModel):
    """QA report over the playable bundle and upstream intent."""

    verdict: str  # pass | needs_work
    summary: str
    issues: list[QaIssue] = Field(default_factory=list)
    checks_run: list[str] = Field(alias="checksRun", default_factory=list)

    model_config = {"populate_by_name": True}


@dataclass(frozen=True)
class QaTeamInput:
    prompt: str
    vision_summary: str
    core_loop: str
    experience_milestones: tuple[str, ...]
    bundle_title: str
    bundle_summary: str
    bundle_implemented: tuple[str, ...]
    platform_count: int
    has_entry_source: bool
    player_start: tuple[int, int]
    goal: tuple[int, int, int, int]


@dataclass(frozen=True)
class QaTeamOutput:
    qa_issues: QaIssues

from gamebuilder.team.qa.domain.model import QaIssue, QaIssues, QaTeamInput, QaTeamOutput


class DeterministicQaAgentGraph:
    def run(self, input: QaTeamInput) -> QaTeamOutput:
        issues: list[QaIssue] = []
        checks = [
            "entrySource present",
            "platforms present",
            "goal present",
            "core loop mentioned in bundle",
        ]

        if not input.has_entry_source:
            issues.append(
                QaIssue(
                    title="Missing playable script",
                    severity="blocker",
                    description="GameBundle has no entrySource for the play cabinet.",
                    repro="Open Play; cabinet fails to boot.",
                    suggested_fix_team="engineering",
                )
            )

        if input.platform_count < 1:
            issues.append(
                QaIssue(
                    title="No solid platforms",
                    severity="blocker",
                    description="Level has no platforms; player cannot stand.",
                    repro="Inspect GameBundle.platforms.",
                    suggested_fix_team="engineering",
                )
            )

        gx, gy, gw, gh = input.goal
        if gw <= 0 or gh <= 0:
            issues.append(
                QaIssue(
                    title="Invalid goal",
                    severity="blocker",
                    description="Goal rectangle has non-positive size.",
                    repro="Inspect GameBundle.goal.",
                    suggested_fix_team="engineering",
                )
            )

        loop = (input.core_loop or "").lower()
        bundle_blob = f"{input.bundle_summary} {' '.join(input.bundle_implemented)}".lower()
        if loop and not any(token in bundle_blob for token in loop.split()[:3] if len(token) > 3):
            issues.append(
                QaIssue(
                    title="Core loop weakly reflected",
                    severity="minor",
                    description=(
                        "Bundle summary/implemented list does not clearly echo "
                        "the design core loop."
                    ),
                    repro="Compare MechanicsSpec.coreLoop to GameBundle.summary.",
                    suggested_fix_team="engineering",
                )
            )

        if not input.experience_milestones:
            issues.append(
                QaIssue(
                    title="No experience milestones to validate against",
                    severity="note",
                    description="Story did not provide milestones; QA used vision only.",
                    suggested_fix_team="story",
                )
            )

        blocking = {i.severity for i in issues} & {"blocker", "major"}
        verdict = "needs_work" if blocking else "pass"
        summary = (
            f"Deterministic QA for “{input.bundle_title or input.prompt}”: "
            f"{len(issues)} issue(s), verdict={verdict}."
        )
        return QaTeamOutput(
            qa_issues=QaIssues(
                verdict=verdict,
                summary=summary,
                issues=issues,
                checks_run=checks,
            )
        )

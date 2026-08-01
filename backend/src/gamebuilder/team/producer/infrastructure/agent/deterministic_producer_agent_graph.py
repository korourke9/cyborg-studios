from gamebuilder.team.producer.domain.model import (
    CoherenceReview,
    ProducerNotes,
    ProducerTeamInput,
    ProducerTeamOutput,
)


class DeterministicProducerAgentGraph:
    def run(self, input: ProducerTeamInput) -> ProducerTeamOutput:
        has_build = bool(input.bundle_title or input.bundle_summary)
        qa_pass = input.qa_verdict.strip().lower() == "pass"
        aligned = has_build and qa_pass

        strengths: list[str] = []
        gaps: list[str] = []
        if input.vision_summary:
            strengths.append("Vision is present and readable.")
        if input.core_loop:
            strengths.append("Core loop is stated.")
        if has_build:
            strengths.append(f"Playable build exists (“{input.bundle_title}”).")
        if qa_pass:
            strengths.append("QA verdict is pass.")
        else:
            gaps.append(
                f"QA is “{input.qa_verdict or 'unknown'}” "
                f"with {input.qa_issue_count} issue(s)."
            )
        if not has_build:
            gaps.append("No GameBundle summary to ship.")

        if aligned:
            decision = "ship"
            rationale = (
                "Teams line up enough for an MVP playable: vision, build, and "
                "QA pass. Ship the cabinet build and gather human feedback."
            )
            next_actions = [
                "Invite a human playtest in the Play cabinet",
                "Capture feel notes for the next pass",
            ]
            cuts: list[str] = []
            celebrate = f"Greenlight for “{input.bundle_title or input.prompt}”."
        elif has_build:
            decision = "revise"
            rationale = (
                "A build exists but coherence or QA still has gaps worth a "
                "focused revise before calling it done."
            )
            next_actions = [
                "Address QA issues with the suggested fix teams",
                "Re-run Producer after the next Engineering/QA pass",
            ]
            cuts = []
            celebrate = "Close — keep the fantasy, tighten the gaps."
        else:
            decision = "cut"
            rationale = "No playable build to evaluate; cannot ship."
            next_actions = ["Re-run Engineering to produce a GameBundle"]
            cuts = ["Ship call until a build exists"]
            celebrate = ""

        return ProducerTeamOutput(
            coherence_review=CoherenceReview(
                aligned=aligned,
                strengths=strengths,
                gaps=gaps,
                summary=(
                    f"Producer coherence for “{input.prompt}”: "
                    f"{'aligned' if aligned else 'needs attention'}."
                ),
            ),
            producer_notes=ProducerNotes(
                decision=decision,
                rationale=rationale,
                cuts=cuts,
                next_actions=next_actions,
                celebrate=celebrate,
            ),
        )

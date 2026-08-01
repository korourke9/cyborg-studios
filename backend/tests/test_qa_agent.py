from gamebuilder.team.qa.domain.model import QaTeamInput
from gamebuilder.team.qa.infrastructure.agent.deterministic_qa_agent_graph import (
    DeterministicQaAgentGraph,
)


def test_deterministic_qa_passes_healthy_bundle() -> None:
    output = DeterministicQaAgentGraph().run(
        QaTeamInput(
            prompt="A tiny robot adventure",
            vision_summary="A focused 2D platformer.",
            core_loop="Jump across platforms to the glow",
            experience_milestones=("Learn jump", "Reach glow"),
            bundle_title="Tiny robot",
            bundle_summary="Jump across platforms to the glow in a short slice.",
            bundle_implemented=("run", "jump", "goal"),
            platform_count=4,
            has_entry_source=True,
            player_start=(80, 340),
            goal=(700, 180, 36, 36),
        )
    )
    assert output.qa_issues.verdict == "pass"
    assert "entrySource present" in output.qa_issues.checks_run


def test_deterministic_qa_flags_missing_script() -> None:
    output = DeterministicQaAgentGraph().run(
        QaTeamInput(
            prompt="Broken",
            vision_summary="",
            core_loop="",
            experience_milestones=(),
            bundle_title="Broken",
            bundle_summary="",
            bundle_implemented=(),
            platform_count=2,
            has_entry_source=False,
            player_start=(0, 0),
            goal=(10, 10, 20, 20),
        )
    )
    assert output.qa_issues.verdict == "needs_work"
    assert any(issue.severity == "blocker" for issue in output.qa_issues.issues)

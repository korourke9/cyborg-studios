from gamebuilder.team.producer.domain.model import ProducerTeamInput
from gamebuilder.team.producer.infrastructure.agent.deterministic_producer_agent_graph import (
    DeterministicProducerAgentGraph,
)


def test_deterministic_producer_ships_when_qa_passes() -> None:
    output = DeterministicProducerAgentGraph().run(
        ProducerTeamInput(
            prompt="A tiny robot adventure",
            vision_summary="A focused 2D platformer.",
            design_pillars=("Readable jumps", "Warm curiosity"),
            core_loop="Jump to the glow",
            narrative_tone="Warm",
            setting="Crystal tunnels",
            art_mood="Curious",
            bundle_title="Tiny robot",
            bundle_summary="A short readable platforming slice.",
            qa_verdict="pass",
            qa_summary="Looks good",
            qa_issue_count=0,
        )
    )
    assert output.coherence_review.aligned is True
    assert output.producer_notes.decision == "ship"


def test_deterministic_producer_revises_when_qa_fails() -> None:
    output = DeterministicProducerAgentGraph().run(
        ProducerTeamInput(
            prompt="Rough draft",
            vision_summary="Something",
            design_pillars=(),
            core_loop="Run",
            narrative_tone="",
            setting="",
            art_mood="",
            bundle_title="Rough",
            bundle_summary="Exists",
            qa_verdict="needs_work",
            qa_summary="Blockers found",
            qa_issue_count=2,
        )
    )
    assert output.coherence_review.aligned is False
    assert output.producer_notes.decision == "revise"

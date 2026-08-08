from gamebuilder.evals.run_structural_eval import (
    GOLDEN_PROMPTS,
    score_project_payload,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.evals.run_structural_eval import describe_resolved_runtimes


def test_golden_prompts_non_empty() -> None:
    assert len(GOLDEN_PROMPTS) >= 3


def test_describe_runtimes_includes_all_teams() -> None:
    rows = describe_resolved_runtimes(Settings())
    ids = {row["team"] for row in rows}
    assert ids == {"design", "story", "art", "engineering", "qa", "producer"}
    art = next(row for row in rows if row["team"] == "art")
    assert "hero" in art["image_roles"]


def test_structural_score_detects_missing_types() -> None:
    score = score_project_payload(
        "demo",
        {"status": "DONE", "artifacts": [{"type": "VISION_DOC", "payload": "{}"}]},
    )
    assert score.passed is False
    assert "GAME_BUNDLE" in score.missing_types

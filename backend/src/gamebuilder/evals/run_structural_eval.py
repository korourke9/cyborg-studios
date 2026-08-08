"""Golden-prompt structural eval for provider A/B (deterministic / local / paid).

Usage (from backend/):
  .venv/bin/python -m gamebuilder.evals.run_structural_eval

Scores artifact presence and schema basics without calling live LLMs by default.
Set EVAL_MODE=local|paid and configure LLM_*/IMAGE_* to exercise live stacks.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gamebuilder.orchestration.infrastructure.config.agent_runtime import all_team_specs
from gamebuilder.orchestration.infrastructure.config.settings import Settings
from gamebuilder.orchestration.infrastructure.config.agent_runtime import (
    resolve_agent_runtime,
)

REQUIRED_ARTIFACT_TYPES = {
    "VISION_DOC",
    "DESIGN_PILLARS",
    "MECHANICS_SPEC",
    "SYSTEMS_SPEC",
    "NARRATIVE_SPEC",
    "EXPERIENCE_MILESTONES",
    "ART_DIRECTION",
    "ASSET_LIST",
    "ASSET_PROMPTS",
    "GAME_BUNDLE",
    "QA_ISSUES",
    "COHERENCE_REVIEW",
    "PRODUCER_NOTES",
}

GOLDEN_PROMPTS = (
    "A tiny robot adventure in a glowing cave",
    "A fox courier racing rooftops at dusk",
    "A haunted lighthouse with floating platforms",
)


@dataclass
class StructuralScore:
    prompt: str
    passed: bool
    missing_types: list[str]
    notes: list[str]


def score_project_payload(prompt: str, payload: dict[str, Any]) -> StructuralScore:
    artifacts = payload.get("artifacts") or []
    types = {str(a.get("type")) for a in artifacts if isinstance(a, dict)}
    missing = sorted(REQUIRED_ARTIFACT_TYPES - types)
    notes: list[str] = []

    if payload.get("status") != "DONE":
        notes.append(f"status={payload.get('status')!r} (expected DONE)")

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        if artifact.get("type") != "GAME_BUNDLE":
            continue
        try:
            body = json.loads(str(artifact.get("payload") or "{}"))
        except json.JSONDecodeError:
            notes.append("GAME_BUNDLE payload is not JSON")
            continue
        if not body.get("entrySource") and not body.get("entry_source"):
            notes.append("GAME_BUNDLE missing entrySource")
        platforms = body.get("platforms")
        if not isinstance(platforms, list) or len(platforms) < 1:
            notes.append("GAME_BUNDLE missing platforms")

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        if artifact.get("type") != "QA_ISSUES":
            continue
        try:
            body = json.loads(str(artifact.get("payload") or "{}"))
        except json.JSONDecodeError:
            notes.append("QA_ISSUES payload is not JSON")
            continue
        if body.get("verdict") not in {"pass", "needs_work"}:
            notes.append(f"QA verdict unexpected: {body.get('verdict')!r}")

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        if artifact.get("type") != "PRODUCER_NOTES":
            continue
        try:
            body = json.loads(str(artifact.get("payload") or "{}"))
        except json.JSONDecodeError:
            notes.append("PRODUCER_NOTES payload is not JSON")
            continue
        if body.get("decision") not in {"ship", "revise", "cut"}:
            notes.append(f"Producer decision unexpected: {body.get('decision')!r}")

    passed = not missing and not notes
    return StructuralScore(
        prompt=prompt, passed=passed, missing_types=missing, notes=notes
    )


def describe_resolved_runtimes(settings: Settings) -> list[dict[str, Any]]:
    rows = []
    for spec in all_team_specs():
        runtime = resolve_agent_runtime(spec, settings)
        rows.append(
            {
                "team": runtime.team_id,
                "mode": runtime.mode,
                "model": runtime.model_id,
                "capability": runtime.chat_capability.value,
                "image_roles": list(runtime.image_roles),
                "image_generation_enabled": runtime.image_generation_enabled,
            }
        )
    return rows


def write_runtime_snapshot(out_dir: Path, settings: Settings) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "runtimes.json"
    path.write_text(
        json.dumps(
            {
                "llm_provider": settings.normalized_llm_provider(),
                "image_provider": settings.normalized_image_provider(),
                "teams": describe_resolved_runtimes(settings),
                "golden_prompts": list(GOLDEN_PROMPTS),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def main() -> None:
    settings = Settings()
    out = Path("evals/out/latest")
    path = write_runtime_snapshot(out, settings)
    print(f"Wrote runtime snapshot to {path}")
    print("Teams:")
    for row in describe_resolved_runtimes(settings):
        print(
            f"  {row['team']}: mode={row['mode']} model={row['model']} "
            f"images={row['image_generation_enabled']}"
        )
    print(
        "\nTo score a finished project JSON, load it and call "
        "score_project_payload(prompt, payload)."
    )


if __name__ == "__main__":
    main()

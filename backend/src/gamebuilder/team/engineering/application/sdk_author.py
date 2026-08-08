"""LLM authorship of constrained Cyborg Phaser SDK JavaScript."""

from __future__ import annotations

import json
import logging
import re

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_sync import run_agent_sync
from gamebuilder.team.engineering.application.sdk_from_ir import (
    compile_sdk_source_from_bundle,
)
from gamebuilder.team.engineering.application.sdk_lint import lint_sdk_javascript
from gamebuilder.team.engineering.domain.model import EngineeringTeamInput, GameBundle

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are the Engineering gameplay author for Cyborg Studios. "
    "You write sandboxed Phaser 3 game JavaScript that runs inside Cyborg.boot. "
    "You must invent gameplay that is meaningfully different from a plain "
    "static platformer when the brief allows it — moving hazards, patrol enemies, "
    "double jump, timers, alternate win rules, or custom Phaser scene logic. "
    "Respond with JSON only matching the schema. "
    "The javascript field must be executable JS only (no markdown fences)."
)

_FENCE_RE = re.compile(
    r"```(?:javascript|js)?\s*([\s\S]*?)```", re.IGNORECASE
)


class SdkAuthoredScript(BaseModel):
    javascript: str = Field(
        description="Complete Cyborg.boot(...) script, no markdown fences"
    )
    gameplay_notes: list[str] = Field(
        default_factory=list,
        description="Short notes describing how this SDK build differs from plain IR",
    )


def extract_sdk_javascript(raw: str) -> str:
    """Normalize LLM output into a bare Cyborg.boot script."""
    text = (raw or "").strip()
    if not text:
        return ""
    fenced = _FENCE_RE.search(text)
    if fenced:
        text = fenced.group(1).strip()
    # Drop leading prose before Cyborg.boot if present.
    boot = text.find("Cyborg.boot")
    if boot > 0:
        text = text[boot:].strip()
    return text


def _level_json_for_prompt(bundle: GameBundle) -> str:
    physics = {
        "snappy": {"gravity": 1100, "move": 200, "jump": -380},
        "floaty": {"gravity": 650, "move": 170, "jump": -300},
        "heavy": {"gravity": 1400, "move": 150, "jump": -320},
    }.get(bundle.physics_profile, {"gravity": 1100, "move": 200, "jump": -380})
    level = {
        "title": bundle.title,
        "backgroundHex": bundle.background_hex,
        "playerHex": bundle.player_hex,
        "platformHex": bundle.platform_hex,
        "goalHex": bundle.goal_hex,
        "playerStartX": bundle.player_start_x,
        "playerStartY": bundle.player_start_y,
        "worldWidth": bundle.world_width,
        "worldHeight": bundle.world_height,
        "move": physics["move"],
        "jump": physics["jump"],
        "gravity": physics["gravity"],
        "platforms": [p.model_dump() for p in bundle.platforms],
        "hazards": [h.model_dump() for h in bundle.hazards],
        "collectibles": [c.model_dump() for c in bundle.collectibles],
        "goal": bundle.goal.model_dump(),
        "textures": {
            "hero": bundle.hero_texture_url,
            "backdrop": bundle.backdrop_texture_url,
            "hazard": bundle.hazard_texture_url,
            "platform": bundle.platform_texture_url,
            "collectible": bundle.collectible_texture_url,
        },
        "doubleJump": False,
        "maxTimeSec": 0,
        "requireAllCollectibles": bool(bundle.collectibles),
        "movingHazards": [],
        "enemies": [],
        "heroDisplayW": bundle.hero_display_w,
        "heroDisplayH": bundle.hero_display_h,
        "hazardDisplayW": bundle.hazard_display_w,
        "hazardDisplayH": bundle.hazard_display_h,
        "collectibleDisplayW": bundle.collectible_display_w,
        "collectibleDisplayH": bundle.collectible_display_h,
    }
    return json.dumps(level, indent=2)


def author_user_prompt(
    input: EngineeringTeamInput, bundle: GameBundle, *, lint_feedback: str = ""
) -> str:
    feedback = (
        f"\nPrevious script failed lint/security. Fix these issues:\n{lint_feedback}\n"
        if lint_feedback
        else ""
    )
    return (
        "Write a Cyborg SDK game script for this project.\n"
        f"Prompt: {input.prompt}\n"
        f"Vision: {input.vision_summary}\n"
        f"Core loop: {input.core_loop}\n"
        f"Tone: {input.narrative_tone}\n"
        f"Setting: {input.setting}\n"
        f"{feedback}\n"
        "API (only):\n"
        "  Cyborg.boot(function (api) { ... })\n"
        "  api.createPlatformerFromLevel(levelObject)\n"
        "  api.Phaser  // Phaser 3 global if you need a custom scene\n"
        "  api.notify(type, extra)  // optional playframe signals\n"
        "\n"
        "Rules:\n"
        "- javascript MUST call Cyborg.boot(...)\n"
        "- Prefer enriching createPlatformerFromLevel with twists "
        "(movingHazards, enemies, doubleJump, maxTimeSec) OR a custom Phaser scene\n"
        "- Do NOT use eval, Function, fetch, XHR, WebSocket, Worker, import(), "
        "storage, cookies, window.parent/top/opener, or postMessage\n"
        "- Keep the script under ~200 lines\n"
        "- Make gameplay feel authored for this brief — not a clone of the IR template\n"
        "\n"
        "Starting level IR (you may mutate / extend):\n"
        f"{_level_json_for_prompt(bundle)}\n"
        "\n"
        "Example shape:\n"
        "Cyborg.boot(function (api) {\n"
        "  const L = { ...enriched level... };\n"
        "  L.doubleJump = true;\n"
        "  L.movingHazards = [{ x: 400, y: 360, w: 28, h: 28, axis: 'x', min: 320, max: 520, speed: 80 }];\n"
        "  api.createPlatformerFromLevel(L);\n"
        "});\n"
    )


def author_sdk_javascript_with_llm(
    input: EngineeringTeamInput,
    bundle: GameBundle,
    *,
    model: Model,
    model_settings: ModelSettings | None = None,
    max_attempts: int = 2,
) -> tuple[str, list[str], str]:
    """Return (javascript, gameplay_notes, authorship_mode).

    authorship_mode is ``llm`` on success or ``llm_fallback`` if we fall back
    to the IR template after lint failures.
    """
    agent: Agent[None, SdkAuthoredScript] = Agent(
        model,
        output_type=SdkAuthoredScript,
        system_prompt=_SYSTEM,
        model_settings=model_settings,
        retries=2,
    )

    lint_feedback = ""
    last_notes: list[str] = []
    for attempt in range(max_attempts):
        try:
            result = run_agent_sync(
                agent, author_user_prompt(input, bundle, lint_feedback=lint_feedback)
            )
        except Exception:
            logger.exception("SDK LLM authorship failed on attempt %s", attempt + 1)
            break

        source = extract_sdk_javascript(result.javascript)
        last_notes = list(result.gameplay_notes)
        issues = lint_sdk_javascript(source)
        if not issues:
            return source, last_notes, "llm"

        lint_feedback = "\n".join(f"- {issue}" for issue in issues)
        logger.info("SDK authorship lint failed (attempt %s): %s", attempt + 1, issues)

    fallback = compile_sdk_source_from_bundle(bundle)
    notes = [
        *last_notes,
        "Fell back to IR→SDK template after authorship lint failures",
    ]
    return fallback, notes, "llm_fallback"

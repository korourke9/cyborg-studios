"""Deterministic / template SDK JS that uses the Cyborg Phaser facade."""

from __future__ import annotations

import json

from gamebuilder.team.engineering.domain.model import GameBundle

_PHYSICS = {
    "snappy": {"gravity": 1100, "move": 200, "jump": -380},
    "floaty": {"gravity": 650, "move": 170, "jump": -300},
    "heavy": {"gravity": 1400, "move": 150, "jump": -320},
}


def compile_sdk_source_from_bundle(bundle: GameBundle) -> str:
    """Emit SDK JS for the same IR (experiment baseline; LLM may replace later)."""
    physics = _PHYSICS.get(bundle.physics_profile, _PHYSICS["snappy"])
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
        "heroDisplayW": bundle.hero_display_w,
        "heroDisplayH": bundle.hero_display_h,
        "hazardDisplayW": bundle.hazard_display_w,
        "hazardDisplayH": bundle.hazard_display_h,
        "collectibleDisplayW": bundle.collectible_display_w,
        "collectibleDisplayH": bundle.collectible_display_h,
    }
    payload = json.dumps(level, separators=(",", ":"))
    return f"""/* Cyborg SDK experiment — generated from IR */
Cyborg.boot(function (api) {{
  const L = {payload};
  api.createPlatformerFromLevel(L);
}});
"""

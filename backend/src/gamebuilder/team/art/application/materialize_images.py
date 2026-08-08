"""Persist generated art binaries and rewrite AssetList fileRefs."""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from gamebuilder.orchestration.application.port.image_generator import ImageGenerator
from gamebuilder.orchestration.application.team_agent_spec import ResolvedAgentRuntime
from gamebuilder.team.art.application.palette_from_images import (
    palette_from_generated_assets,
)
from gamebuilder.team.art.application.prepare_game_sprites import (
    prepare_game_sprite_file,
)
from gamebuilder.team.art.domain.model import (
    ArtDirection,
    ArtTeamOutput,
    AssetList,
    AssetListItem,
    AssetPromptItem,
)

logger = logging.getLogger(__name__)

# Role → how this image is used in a 2D Phaser platformer (image-model framing).
_ROLE_GAME_CONTEXT: dict[str, str] = {
    "hero": (
        "2D side-view platformer PLAYER SPRITE for a video game: single character, "
        "full body, centered, plain or transparent background, no UI, no text, "
        "no photorealism. Readable silhouette at ~64px for Phaser."
    ),
    "key-level-backdrop": (
        "2D platformer LEVEL BACKGROUND plate for a video game: wide environment "
        "art with empty lower foreground so platforms can sit on top, no UI, "
        "no large foreground characters, parallax-friendly stage backdrop."
    ),
    "signature-hazard": (
        "2D platformer HAZARD PROP/TILE for a video game: one clear danger object "
        "the player must avoid (spikes, crystal, enemy, trap), single subject, "
        "plain or transparent background, instantly readable silhouette."
    ),
    "key-level-tiles": (
        "2D platformer GROUND/PLATFORM TILE set for a video game: solid walkable "
        "ledges and floor pieces, seamless edges, plain background, no characters."
    ),
    "collectible": (
        "2D platformer COLLECTIBLE pickup for a video game: one small shiny item, "
        "centered, plain or transparent background, pops against dark caves."
    ),
}


def compose_game_asset_image_prompt(
    *,
    role: str,
    subject_brief: str,
    art_direction: ArtDirection,
    game_prompt: str = "",
) -> str:
    """Build an image-model prompt that targets usable platformer game art."""
    framing = _ROLE_GAME_CONTEXT.get(
        role,
        (
            "2D platformer video-game asset: single clear subject, plain background, "
            "no UI, no text, readable at small size for Phaser."
        ),
    )
    by_role = {swatch.role.lower(): swatch.hex for swatch in art_direction.palette}
    primary = by_role.get("primary", "")
    secondary = by_role.get("secondary", "")
    accent = by_role.get("accent", "")
    background = by_role.get("background", "")
    ink = by_role.get("ink", "")

    color_line = _role_color_instruction(
        role,
        primary=primary,
        secondary=secondary,
        accent=accent,
        background=background,
        ink=ink,
    )
    palette = ", ".join(f"{swatch.role} {swatch.hex}" for swatch in art_direction.palette)
    parts = [
        framing,
        color_line,
        f"Subject: {subject_brief.strip().rstrip('.')}." if subject_brief.strip() else "",
        f"Game premise: {game_prompt.strip()}." if game_prompt.strip() else "",
        f"Art style: {art_direction.style}." if art_direction.style else "",
        f"Mood: {art_direction.mood}." if art_direction.mood else "",
        f"Studio palette reference: {palette}." if palette else "",
        "Pixel-art-friendly shapes, high contrast, game-ready sprite sheet style.",
    ]
    return " ".join(part for part in parts if part)


def _role_color_instruction(
    role: str,
    *,
    primary: str,
    secondary: str,
    accent: str,
    background: str,
    ink: str,
) -> str:
    if role == "hero" and primary:
        return (
            f"IMPORTANT: paint the character mainly in {primary}"
            + (f" with {accent} glow accents" if accent else "")
            + (f" and {ink} outlines" if ink else "")
            + ". Match these hex colors closely."
        )
    if role == "key-level-backdrop" and background:
        return (
            f"IMPORTANT: dominate the scene with {background}"
            + (f", midtones near {secondary}" if secondary else "")
            + (f", and accents of {accent}" if accent else "")
            + ". Match these hex colors closely."
        )
    if role == "signature-hazard" and (secondary or accent or primary):
        danger = secondary or accent or primary
        return (
            f"IMPORTANT: make the hazard read as {danger}"
            + (f" against darker {ink or background}" if (ink or background) else "")
            + ". Match these hex colors closely."
        )
    if primary or background:
        bits = [c for c in (primary, secondary, accent, background, ink) if c]
        return f"IMPORTANT: use these hex colors prominently: {', '.join(bits)}."
    return ""


def _subject_brief_for_role(
    role: str,
    art_output: ArtTeamOutput,
    prompt_item: AssetPromptItem | None,
) -> str:
    direction = art_output.art_direction
    if prompt_item and prompt_item.prompt.strip():
        brief = prompt_item.prompt.strip()
        # Prefer ArtDirection when the LLM only echoed a short concept phrase.
        if role == "hero" and direction.hero_concept and len(brief) < 40:
            return direction.hero_concept
        if role == "key-level-backdrop" and direction.world_concept and len(brief) < 40:
            return direction.world_concept
        return brief
    if role == "hero":
        return direction.hero_concept
    if role == "key-level-backdrop":
        return direction.world_concept
    if role == "signature-hazard":
        return "Signature hazard that matches the world and threatens readable jumps"
    if role == "key-level-tiles":
        return "Walkable platform tiles that match the world materials"
    if role == "collectible":
        return "Bright collectible that fits the player fantasy"
    return f"Game asset for role {role}"


def materialize_art_images(
    *,
    project_id: UUID,
    art_output: ArtTeamOutput,
    runtime: ResolvedAgentRuntime,
    image_generator: ImageGenerator | None,
    asset_root: Path,
    size: str,
    soft_fail: bool,
    public_api_base_url: str = "http://localhost:8080",
    game_prompt: str = "",
) -> tuple[ArtTeamOutput, list[tuple[str, str, Path, str]]]:
    """Generate images for declared roles.

    Returns updated ArtTeamOutput and list of
    (asset_id, role, absolute_path, content_type) for BINARY_ASSET persistence.
    """
    del public_api_base_url  # relative fileRefs; frontend prefixes API base
    if not runtime.image_generation_enabled or image_generator is None:
        return art_output, []

    prompts_by_role = {
        item.role: item for item in art_output.asset_prompts.prompts
    }

    project_dir = asset_root / str(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    updated_assets: list[AssetListItem] = []
    binary_records: list[tuple[str, str, Path, str]] = []
    generated_ids: set[str] = set()

    def file_ref_for(asset_id: str) -> str:
        # Relative so the browser always uses NEXT_PUBLIC_API_BASE_URL.
        return f"/api/projects/{project_id}/assets/{asset_id}"

    def generate_for(
        asset_id: str, role: str, prompt_item: AssetPromptItem | None
    ) -> AssetListItem | None:
        subject = _subject_brief_for_role(role, art_output, prompt_item)
        full_prompt = compose_game_asset_image_prompt(
            role=role,
            subject_brief=subject,
            art_direction=art_output.art_direction,
            game_prompt=game_prompt,
        )
        try:
            image = image_generator.generate(full_prompt, size=size)
            path = project_dir / f"{asset_id}.png"
            path.write_bytes(image.data)
            frame_w, frame_h = prepare_game_sprite_file(path, role=role)
            binary_records.append((asset_id, role, path, "image/png"))
            generated_ids.add(asset_id)
            return AssetListItem(
                id=asset_id,
                role=role,
                file_ref=file_ref_for(asset_id),
                frame_w=frame_w,
                frame_h=frame_h,
                processed=True,
            )
        except Exception:
            logger.exception(
                "Image generation failed for asset %s role %s", asset_id, role
            )
            if not soft_fail:
                raise
            return None

    for asset in art_output.asset_list.assets:
        if asset.role not in runtime.image_roles:
            updated_assets.append(asset)
            continue

        prompt_item = prompts_by_role.get(asset.role)
        generated = generate_for(asset.id, asset.role, prompt_item)
        updated_assets.append(generated if generated is not None else asset)

    for role in runtime.image_roles:
        if any(a.role == role for a in updated_assets):
            continue
        prompt_item = prompts_by_role.get(role)
        if prompt_item is None:
            continue
        asset_id = prompt_item.asset_id
        if asset_id in generated_ids:
            continue
        generated = generate_for(asset_id, role, prompt_item)
        if generated is not None:
            updated_assets.append(generated)

    direction = art_output.art_direction
    if binary_records:
        role_paths = {role: path for _asset_id, role, path, _ctype in binary_records}
        synced = palette_from_generated_assets(
            role_paths,
            fallback=list(direction.palette),
        )
        direction = ArtDirection(
            style=direction.style,
            palette=synced,
            mood=direction.mood,
            hero_concept=direction.hero_concept,
            world_concept=direction.world_concept,
            key_scenes=direction.key_scenes,
            notes=(
                (direction.notes + " " if direction.notes else "")
                + "Palette synced from generated sprites; sprites cut out and "
                "normalized for Phaser."
            ).strip(),
        )

    return (
        ArtTeamOutput(
            art_direction=direction,
            asset_list=AssetList(assets=updated_assets),
            asset_prompts=art_output.asset_prompts,
        ),
        binary_records,
    )

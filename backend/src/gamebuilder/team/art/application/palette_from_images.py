"""Derive a desk/engineering palette from generated sprite pixels."""

from __future__ import annotations

from collections import Counter
from colorsys import rgb_to_hsv
from pathlib import Path

from gamebuilder.team.art.domain.model import PaletteColor

try:
    from PIL import Image
except ImportError:  # pragma: no cover - optional until pillow is installed
    Image = None  # type: ignore[assignment,misc]


def palette_from_generated_assets(
    role_paths: dict[str, Path],
    *,
    fallback: list[PaletteColor] | None = None,
) -> list[PaletteColor]:
    """Build primary/secondary/accent/background/ink from generated PNGs.

    Stable Diffusion rarely honors hex lists in prompts; sampling the sprites
    keeps the Art desk and Engineering colors aligned with what players see.
    """
    fallback = list(fallback or [])
    if Image is None or not role_paths:
        return fallback or _default_palette()

    by_role: dict[str, list[tuple[int, int, int]]] = {}
    for role, path in role_paths.items():
        if not path.is_file():
            continue
        try:
            colors = _dominant_colors(path, limit=6)
        except Exception:
            continue
        if colors:
            by_role[role] = colors

    if not by_role:
        return fallback or _default_palette()

    hero = by_role.get("hero") or []
    backdrop = by_role.get("key-level-backdrop") or by_role.get("backdrop") or []
    hazard = by_role.get("signature-hazard") or by_role.get("hazard") or []
    all_colors = hero + backdrop + hazard

    primary = _pick_chromatic(hero) or _pick_chromatic(all_colors) or _fallback_hex(
        fallback, "primary", "#9b7ed9"
    )
    secondary = (
        _pick_chromatic(hazard, exclude={primary})
        or _pick_mid(all_colors, exclude={primary})
        or _fallback_hex(fallback, "secondary", "#ff8c42")
    )
    accent = (
        _pick_chromatic(hero, exclude={primary, secondary})
        or _pick_chromatic(all_colors, exclude={primary, secondary})
        or _fallback_hex(fallback, "accent", "#3de7ff")
    )
    background = (
        _pick_background(backdrop)
        or _pick_dark(backdrop or all_colors, exclude={primary, secondary, accent})
        or _fallback_hex(fallback, "background", "#1a1424")
    )
    ink = (
        _pick_dark(all_colors, exclude={primary, secondary, accent, background})
        or _fallback_hex(fallback, "ink", "#120c18")
    )

    return [
        PaletteColor(role="primary", hex=primary),
        PaletteColor(role="secondary", hex=secondary),
        PaletteColor(role="accent", hex=accent),
        PaletteColor(role="background", hex=background),
        PaletteColor(role="ink", hex=ink),
    ]


def _dominant_colors(path: Path, *, limit: int = 6) -> list[tuple[int, int, int]]:
    assert Image is not None
    with Image.open(path) as raw:
        rgba = raw.convert("RGBA")
        # Downsample for speed; BOX keeps blocky sprite hues.
        small = rgba.resize((48, 48), Image.Resampling.BOX)

    opaque: list[tuple[int, int, int]] = []
    for r, g, b, a in small.getdata():
        if a < 32:
            continue
        # Skip near-white studio backgrounds SD often leaves behind.
        if r > 245 and g > 245 and b > 245:
            continue
        opaque.append((r, g, b))

    if not opaque:
        return []

    # Quantize via simple bucket rounding so we don't need Image.quantize quirks.
    buckets: Counter[tuple[int, int, int]] = Counter()
    for r, g, b in opaque:
        buckets[(_bucket(r), _bucket(g), _bucket(b))] += 1

    return [color for color, _ in buckets.most_common(limit)]


def _bucket(channel: int) -> int:
    return min(255, max(0, (channel // 24) * 24 + 12))


def _to_hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def _hsv(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    return rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)


def _pick_chromatic(
    colors: list[tuple[int, int, int]],
    *,
    exclude: set[str] | None = None,
) -> str | None:
    exclude = exclude or set()
    ranked = sorted(
        colors,
        key=lambda c: (_hsv(c)[1], _hsv(c)[2]),
        reverse=True,
    )
    for color in ranked:
        hex_color = _to_hex(color)
        if hex_color in exclude:
            continue
        _h, s, v = _hsv(color)
        if s >= 0.18 and 0.12 <= v <= 0.95:
            return hex_color
    for color in ranked:
        hex_color = _to_hex(color)
        if hex_color not in exclude:
            return hex_color
    return None


def _pick_mid(
    colors: list[tuple[int, int, int]],
    *,
    exclude: set[str] | None = None,
) -> str | None:
    exclude = exclude or set()
    ranked = sorted(colors, key=lambda c: abs(_hsv(c)[2] - 0.55))
    for color in ranked:
        hex_color = _to_hex(color)
        if hex_color not in exclude:
            return hex_color
    return None


def _pick_dark(
    colors: list[tuple[int, int, int]],
    *,
    exclude: set[str] | None = None,
) -> str | None:
    exclude = exclude or set()
    ranked = sorted(colors, key=lambda c: _hsv(c)[2])
    for color in ranked:
        hex_color = _to_hex(color)
        if hex_color not in exclude:
            return hex_color
    return None


def _pick_background(colors: list[tuple[int, int, int]]) -> str | None:
    if not colors:
        return None
    # Prefer a darker, lower-saturation plate color for stage backgrounds.
    ranked = sorted(colors, key=lambda c: (_hsv(c)[1], -_hsv(c)[2]))
    return _to_hex(ranked[0])


def _fallback_hex(fallback: list[PaletteColor], role: str, default: str) -> str:
    for swatch in fallback:
        if swatch.role == role and swatch.hex.startswith("#"):
            return swatch.hex.lower()
    return default


def _default_palette() -> list[PaletteColor]:
    return [
        PaletteColor(role="primary", hex="#9b7ed9"),
        PaletteColor(role="secondary", hex="#ff8c42"),
        PaletteColor(role="accent", hex="#3de7ff"),
        PaletteColor(role="background", hex="#1a1424"),
        PaletteColor(role="ink", hex="#120c18"),
    ]

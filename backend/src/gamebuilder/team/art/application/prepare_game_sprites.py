"""Turn raw image-gen plates into game-ready transparent sprites for Phaser."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpritePrepSpec:
    """How to normalize a role for in-game use."""

    canvas_w: int
    canvas_h: int
    # Backdrop/plates: resize only. Sprites: remove bg + crop + fit.
    cutout: bool = True
    # Corner flood / color distance for cutout (0–255 Euclidean-ish).
    color_tolerance: int = 42
    # Max edge length when cutout is False (backdrop).
    max_edge: int = 1024


# Role → runtime sprite prep. Keep in sync with Engineering display sizes.
ROLE_SPRITE_PREP: dict[str, SpritePrepSpec] = {
    "hero": SpritePrepSpec(canvas_w=64, canvas_h=64, cutout=True, color_tolerance=48),
    "signature-hazard": SpritePrepSpec(
        canvas_w=48, canvas_h=48, cutout=True, color_tolerance=45
    ),
    "hazard": SpritePrepSpec(canvas_w=48, canvas_h=48, cutout=True, color_tolerance=45),
    "collectible": SpritePrepSpec(
        canvas_w=32, canvas_h=32, cutout=True, color_tolerance=45
    ),
    "key-level-tiles": SpritePrepSpec(
        canvas_w=64, canvas_h=64, cutout=True, color_tolerance=40
    ),
    "key-level-backdrop": SpritePrepSpec(
        canvas_w=1024, canvas_h=576, cutout=False, max_edge=1280
    ),
    "backdrop": SpritePrepSpec(
        canvas_w=1024, canvas_h=576, cutout=False, max_edge=1280
    ),
}


def prepare_game_sprite_bytes(data: bytes, *, role: str) -> tuple[bytes, int, int]:
    """Return (png_bytes, frame_w, frame_h). Soft-falls back to original on failure."""
    spec = ROLE_SPRITE_PREP.get(
        role, SpritePrepSpec(canvas_w=64, canvas_h=64, cutout=True)
    )
    try:
        image = Image.open(BytesIO(data)).convert("RGBA")
    except Exception:
        logger.exception("Could not decode image for role %s; leaving raw bytes", role)
        return data, spec.canvas_w, spec.canvas_h

    try:
        if spec.cutout:
            image = _remove_background(image, tolerance=spec.color_tolerance)
            image = _crop_to_alpha(image)
            image = _fit_on_canvas(image, spec.canvas_w, spec.canvas_h)
            frame_w, frame_h = spec.canvas_w, spec.canvas_h
        else:
            image = _fit_max_edge(image, spec.max_edge)
            frame_w, frame_h = image.size

        out = BytesIO()
        image.save(out, format="PNG", optimize=True)
        return out.getvalue(), frame_w, frame_h
    except Exception:
        logger.exception("Sprite prep failed for role %s; leaving raw bytes", role)
        return data, spec.canvas_w, spec.canvas_h


def prepare_game_sprite_file(path: Path, *, role: str) -> tuple[int, int]:
    """Overwrite ``path`` with a game-ready PNG. Returns (frame_w, frame_h)."""
    raw = path.read_bytes()
    prepared, frame_w, frame_h = prepare_game_sprite_bytes(raw, role=role)
    path.write_bytes(prepared)
    return frame_w, frame_h


def _remove_background(image: Image.Image, *, tolerance: int) -> Image.Image:
    """Flood-fill transparency from corners using average corner color."""
    pixels = image.load()
    width, height = image.size
    if width < 2 or height < 2:
        return image

    corners = [
        pixels[0, 0][:3],
        pixels[width - 1, 0][:3],
        pixels[0, height - 1][:3],
        pixels[width - 1, height - 1][:3],
    ]
    target = tuple(sum(c[i] for c in corners) // 4 for i in range(3))

    # Mark near-bg pixels via flood from edges for contiguous bg, then also
    # wipe remaining near-target fringe (common with SD plates).
    mask = Image.new("L", (width, height), 0)
    mask_px = mask.load()
    stack = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
    # Seed more edge points for uneven plates.
    for x in range(0, width, max(1, width // 16)):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(0, height, max(1, height // 16)):
        stack.append((0, y))
        stack.append((width - 1, y))

    seen: set[tuple[int, int]] = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in seen:
            continue
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        seen.add((x, y))
        r, g, b, a = pixels[x, y]
        if a < 8:
            mask_px[x, y] = 255
            continue
        if _color_dist((r, g, b), target) > tolerance:
            continue
        mask_px[x, y] = 255
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    # Soft fringe wipe: any remaining near-bg becomes transparent.
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if mask_px[x, y] == 255 or (
                a > 0 and _color_dist((r, g, b), target) <= tolerance
            ):
                pixels[x, y] = (r, g, b, 0)

    # Slight blur on alpha edge reduces jagged cutouts.
    alpha = image.getchannel("A").filter(ImageFilter.SMOOTH)
    image.putalpha(alpha)
    return image


def _crop_to_alpha(image: Image.Image, *, pad: int = 2) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        return image
    left, top, right, bottom = bbox
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(image.width, right + pad)
    bottom = min(image.height, bottom + pad)
    return image.crop((left, top, right, bottom))


def _fit_on_canvas(image: Image.Image, canvas_w: int, canvas_h: int) -> Image.Image:
    fitted = image.copy()
    fitted.thumbnail((canvas_w, canvas_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    ox = (canvas_w - fitted.width) // 2
    oy = (canvas_h - fitted.height) // 2
    canvas.paste(fitted, (ox, oy), fitted)
    return canvas


def _fit_max_edge(image: Image.Image, max_edge: int) -> Image.Image:
    w, h = image.size
    longest = max(w, h)
    if longest <= max_edge:
        return image
    scale = max_edge / float(longest)
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def _color_dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return (
        (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2
    ) ** 0.5

from io import BytesIO
from pathlib import Path

from PIL import Image

from gamebuilder.team.art.application.prepare_game_sprites import (
    prepare_game_sprite_bytes,
    prepare_game_sprite_file,
)


def _solid_plate(color: tuple[int, int, int], subject: tuple[int, int, int]) -> bytes:
    """Opaque plate with a colored subject in the center (simulates SD output)."""
    image = Image.new("RGBA", (128, 128), (*color, 255))
    for y in range(40, 88):
        for x in range(48, 80):
            image.putpixel((x, y), (*subject, 255))
    out = BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def test_prepare_hero_cutout_and_canvas() -> None:
    raw = _solid_plate((240, 240, 240), (155, 126, 217))
    prepared, frame_w, frame_h = prepare_game_sprite_bytes(raw, role="hero")
    assert frame_w == 64
    assert frame_h == 64
    image = Image.open(BytesIO(prepared)).convert("RGBA")
    assert image.size == (64, 64)
    # Corners of the canvas should be transparent after cutout + fit.
    assert image.getpixel((0, 0))[3] == 0
    # Center should keep subject opacity.
    cx, cy = image.size[0] // 2, image.size[1] // 2
    assert image.getpixel((cx, cy))[3] > 0


def test_prepare_backdrop_keeps_plate_without_cutout() -> None:
    raw = _solid_plate((30, 20, 40), (80, 60, 100))
    prepared, frame_w, frame_h = prepare_game_sprite_bytes(
        raw, role="key-level-backdrop"
    )
    image = Image.open(BytesIO(prepared)).convert("RGBA")
    assert image.size == (frame_w, frame_h)
    # Backdrop path does not flood-clear corners.
    assert image.getpixel((0, 0))[3] == 255


def test_prepare_file_overwrite(tmp_path: Path) -> None:
    path = tmp_path / "player.png"
    path.write_bytes(_solid_plate((250, 250, 250), (200, 80, 40)))
    frame_w, frame_h = prepare_game_sprite_file(path, role="signature-hazard")
    assert frame_w == 48
    assert frame_h == 48
    image = Image.open(path).convert("RGBA")
    assert image.size == (48, 48)


def test_prepare_invalid_bytes_soft_fails() -> None:
    prepared, frame_w, frame_h = prepare_game_sprite_bytes(b"not-an-image", role="hero")
    assert prepared == b"not-an-image"
    assert frame_w == 64
    assert frame_h == 64

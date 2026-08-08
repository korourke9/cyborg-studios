from pathlib import Path

from PIL import Image

from gamebuilder.team.art.application.palette_from_images import (
    palette_from_generated_assets,
)
from gamebuilder.team.art.domain.model import PaletteColor


def _solid_png(path: Path, rgb: tuple[int, int, int]) -> None:
    Image.new("RGB", (32, 32), rgb).save(path)


def test_palette_from_generated_assets_maps_roles(tmp_path: Path) -> None:
    hero = tmp_path / "hero.png"
    backdrop = tmp_path / "bg.png"
    hazard = tmp_path / "hazard.png"
    _solid_png(hero, (40, 180, 220))  # cyan-ish primary
    _solid_png(backdrop, (20, 16, 40))  # dark cave bg
    _solid_png(hazard, (220, 90, 40))  # orange hazard

    palette = palette_from_generated_assets(
        {
            "hero": hero,
            "key-level-backdrop": backdrop,
            "signature-hazard": hazard,
        },
        fallback=[
            PaletteColor(role="primary", hex="#ffffff"),
            PaletteColor(role="secondary", hex="#ffffff"),
            PaletteColor(role="accent", hex="#ffffff"),
            PaletteColor(role="background", hex="#ffffff"),
            PaletteColor(role="ink", hex="#ffffff"),
        ],
    )
    by_role = {swatch.role: swatch.hex for swatch in palette}
    assert by_role["primary"].startswith("#")
    assert by_role["background"].startswith("#")
    # Backdrop is dark → background should stay dark (low value).
    bg = by_role["background"].lstrip("#")
    br, bg_g, bb = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    assert (br + bg_g + bb) / 3 < 80
    # Hero cyan-ish should not collapse to white fallback.
    assert by_role["primary"].lower() != "#ffffff"


def test_palette_falls_back_without_images() -> None:
    fallback = [PaletteColor(role="primary", hex="#abcdef")]
    palette = palette_from_generated_assets({}, fallback=fallback)
    assert palette[0].hex == "#abcdef"

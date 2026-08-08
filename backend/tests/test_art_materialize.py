from pathlib import Path
from uuid import uuid4

from gamebuilder.orchestration.application.port.image_generator import GeneratedImage
from gamebuilder.orchestration.application.team_agent_spec import ResolvedAgentRuntime
from gamebuilder.orchestration.application.port.llm import ModelCapability
from gamebuilder.team.art.application.materialize_images import (
    compose_game_asset_image_prompt,
    materialize_art_images,
)
from gamebuilder.team.art.domain.model import (
    ArtDirection,
    ArtTeamOutput,
    AssetList,
    AssetListItem,
    AssetPromptItem,
    AssetPrompts,
    PaletteColor,
)


class FakeImageGenerator:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str, *, size: str = "512x512") -> GeneratedImage:
        self.prompts.append(prompt)
        return GeneratedImage(data=b"fakepng", content_type="image/png")


def _sample_output() -> ArtTeamOutput:
    return ArtTeamOutput(
        art_direction=ArtDirection(
            style="pixel soft",
            palette=[PaletteColor(role="primary", hex="#9b7ed9")],
            mood="curious",
            hero_concept="tiny robot",
            world_concept="glow caves",
            key_scenes=["reveal", "safe room"],
        ),
        asset_list=AssetList(
            assets=[
                AssetListItem(id="player", role="hero", file_ref="placeholder://hero"),
                AssetListItem(
                    id="background",
                    role="key-level-backdrop",
                    file_ref="placeholder://bg",
                ),
                AssetListItem(
                    id="hazard",
                    role="signature-hazard",
                    file_ref="placeholder://hazard",
                ),
                AssetListItem(id="tiles", role="key-level-tiles", file_ref="placeholder://tiles"),
            ]
        ),
        asset_prompts=AssetPrompts(
            prompts=[
                AssetPromptItem(asset_id="player", role="hero", prompt="hero sheet"),
                AssetPromptItem(
                    asset_id="background",
                    role="key-level-backdrop",
                    prompt="backdrop",
                ),
                AssetPromptItem(
                    asset_id="hazard", role="signature-hazard", prompt="hazard"
                ),
            ]
        ),
    )


def test_compose_game_asset_prompt_includes_platformer_context() -> None:
    direction = ArtDirection(
        style="pixel soft",
        palette=[PaletteColor(role="primary", hex="#9b7ed9")],
        mood="curious",
        hero_concept="tiny robot",
        world_concept="glow caves",
        key_scenes=["reveal"],
    )
    prompt = compose_game_asset_image_prompt(
        role="hero",
        subject_brief="tiny glowing robot with oversized boots",
        art_direction=direction,
        game_prompt="A tiny robot adventure in a glowing cave",
    )
    assert "PLAYER SPRITE" in prompt or "platformer" in prompt.lower()
    assert "Phaser" in prompt
    assert "#9b7ed9" in prompt
    assert "glowing cave" in prompt


def test_materialize_rewrites_image_roles(tmp_path: Path) -> None:
    runtime = ResolvedAgentRuntime(
        team_id="art",
        mode="deterministic",
        model_id="llama3.2",
        chat_capability=ModelCapability.ART,
        image_roles=("hero", "key-level-backdrop", "signature-hazard"),
        image_generation_enabled=True,
    )
    project_id = uuid4()
    fake = FakeImageGenerator()
    updated, binaries = materialize_art_images(
        project_id=project_id,
        art_output=_sample_output(),
        runtime=runtime,
        image_generator=fake,
        asset_root=tmp_path,
        size="512x512",
        soft_fail=False,
        public_api_base_url="http://localhost:8080",
        game_prompt="A tiny robot adventure in a glowing cave",
    )
    assert len(binaries) == 3
    by_role = {a.role: a for a in updated.asset_list.assets}
    assert by_role["hero"].file_ref == f"/api/projects/{project_id}/assets/player"
    assert by_role["key-level-tiles"].file_ref.startswith("placeholder://")
    # Invalid fake PNG bytes soft-fail sprite prep but still mark processed sizes.
    assert by_role["hero"].frame_w == 64
    assert by_role["hero"].frame_h == 64
    assert by_role["hero"].processed is True
    assert (tmp_path / str(project_id) / "player.png").read_bytes() == b"fakepng"
    assert any("PLAYER SPRITE" in p or "platformer" in p.lower() for p in fake.prompts)
    assert any("glowing cave" in p for p in fake.prompts)
    assert any("IMPORTANT" in p and "#9b7ed9" in p for p in fake.prompts)
    # Fake PNG bytes aren't valid images — palette sync should soft-keep fallback.
    assert updated.art_direction.palette[0].hex == "#9b7ed9"


def test_materialize_noop_when_images_disabled(tmp_path: Path) -> None:
    runtime = ResolvedAgentRuntime(
        team_id="art",
        mode="deterministic",
        model_id="llama3.2",
        chat_capability=ModelCapability.ART,
        image_roles=("hero",),
        image_generation_enabled=False,
    )
    original = _sample_output()
    updated, binaries = materialize_art_images(
        project_id=uuid4(),
        art_output=original,
        runtime=runtime,
        image_generator=FakeImageGenerator(),
        asset_root=tmp_path,
        size="512x512",
        soft_fail=True,
    )
    assert binaries == []
    assert updated.asset_list.assets[0].file_ref.startswith("placeholder://")

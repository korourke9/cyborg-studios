from gamebuilder.team.engineering.application.engineers_agent_service import (
    EngineersAgentService,
)
from gamebuilder.team.engineering.application.lab_options import EngineeringLabOptions
from gamebuilder.team.engineering.application.sdk_author import extract_sdk_javascript
from gamebuilder.team.engineering.application.sdk_from_ir import (
    compile_sdk_source_from_bundle,
)
from gamebuilder.team.engineering.application.sdk_lint import lint_sdk_javascript
from gamebuilder.team.engineering.application.sdk_security_review import (
    review_sdk_javascript_static,
)
from gamebuilder.team.engineering.domain.model import EngineeringTeamInput
from gamebuilder.team.engineering.infrastructure.agent.deterministic_engineering_agent_graph import (
    DeterministicEngineeringAgentGraph,
)


def _sample_input(**overrides: str) -> EngineeringTeamInput:
    base = dict(
        prompt="A tiny robot adventure in a glowing cave",
        vision_summary="A focused 2D platformer in a glowing cave.",
        core_loop="Jump across platforms to the glow",
        narrative_tone="Warm and lightly heroic",
        setting="Crystal tunnels",
        art_style="Readable soft pixel shapes",
        background_hex="#fff4e8",
        player_hex="#9b7ed9",
        platform_hex="#3a2a4a",
        goal_hex="#ff8c42",
    )
    base.update(overrides)
    return EngineeringTeamInput(**base)


def test_deterministic_engineering_agent_produces_playable_bundle() -> None:
    output = DeterministicEngineeringAgentGraph().run(_sample_input())
    bundle = output.game_bundle
    assert bundle.engine == "phaser3"
    assert len(bundle.platforms) >= 2
    assert len(bundle.hazards) >= 1
    assert len(bundle.collectibles) >= 1
    assert bundle.world_width > 800
    assert bundle.goal.w > 0
    assert "Phaser.Game" in bundle.entry_source
    assert "game-root" in bundle.entry_source
    assert "hazards" in bundle.entry_source
    assert bundle.player_hex == "#9b7ed9"


def test_sdk_lint_accepts_cyborg_boot_template() -> None:
    bundle = DeterministicEngineeringAgentGraph().run(_sample_input(prompt="Gem run")).game_bundle
    source = compile_sdk_source_from_bundle(bundle)
    assert lint_sdk_javascript(source) == []
    assert review_sdk_javascript_static(source).verdict == "allow"


def test_sdk_lint_denies_fetch_and_eval() -> None:
    bad = "Cyborg.boot(function (api) { eval('1'); fetch('/x'); });"
    issues = lint_sdk_javascript(bad)
    assert any("eval" in i.lower() for i in issues)
    assert any("fetch" in i.lower() for i in issues)


def test_extract_sdk_javascript_strips_fences() -> None:
    raw = "Here you go:\n```javascript\nCyborg.boot(function (api) { api.createPlatformerFromLevel({}); });\n```\n"
    cleaned = extract_sdk_javascript(raw)
    assert cleaned.startswith("Cyborg.boot")
    assert "```" not in cleaned


def test_engineers_service_attaches_reviewed_sdk_template() -> None:
    lab = EngineeringLabOptions(
        sdk_enabled=True, sdk_llm_review=False, sdk_llm_authorship=False
    )
    service = EngineersAgentService(
        DeterministicEngineeringAgentGraph(),
        lab_options=lab,
        security_review_model=None,
        authorship_model=None,
    )
    bundle = service.generate_bundle(_sample_input(prompt="Dual runtime experiment")).game_bundle
    assert "Phaser.Game" in bundle.entry_source
    assert "Cyborg.boot" in bundle.sdk_source
    assert bundle.sdk_review_verdict == "allow"
    assert bundle.sdk_authorship == "template"
    assert bundle.playable_runtimes() == ["ir", "sdk"]


def test_engineers_service_respects_lab_sdk_disabled() -> None:
    lab = EngineeringLabOptions(sdk_enabled=False)
    service = EngineersAgentService(
        DeterministicEngineeringAgentGraph(),
        lab_options=lab,
        security_review_model=None,
    )
    bundle = service.generate_bundle(_sample_input(prompt="No SDK")).game_bundle
    assert bundle.sdk_source == ""
    assert bundle.sdk_review_verdict == "skipped"
    assert bundle.sdk_authorship == "none"
    assert bundle.playable_runtimes() == ["ir"]

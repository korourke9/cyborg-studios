from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from gamebuilder.team.engineering.application.lab_options import (
    DEFAULT_LAB_OPTIONS,
    EngineeringLabOptions,
)
from gamebuilder.team.engineering.application.phaser_entry import with_compiled_entry
from gamebuilder.team.engineering.application.port.engineering_agent_graph import (
    EngineeringAgentGraph,
)
from gamebuilder.team.engineering.application.sdk_author import (
    author_sdk_javascript_with_llm,
)
from gamebuilder.team.engineering.application.sdk_from_ir import (
    compile_sdk_source_from_bundle,
)
from gamebuilder.team.engineering.application.sdk_security_review import (
    review_sdk_javascript_static,
    review_sdk_javascript_with_llm,
)
from gamebuilder.team.engineering.domain.model import (
    EngineeringTeamInput,
    EngineeringTeamOutput,
    GameBundle,
)


class EngineersAgentService:
    def __init__(
        self,
        engineering_agent_graph: EngineeringAgentGraph,
        *,
        lab_options: EngineeringLabOptions | None = None,
        security_review_model: Model | None = None,
        authorship_model: Model | None = None,
        model_settings: ModelSettings | None = None,
        # Deprecated: prefer lab_options.sdk_enabled
        sdk_enabled: bool | None = None,
    ) -> None:
        self._engineering_agent_graph = engineering_agent_graph
        self._lab = lab_options or DEFAULT_LAB_OPTIONS
        if sdk_enabled is not None:
            self._lab.sdk_enabled = sdk_enabled
        self._security_review_model = security_review_model
        self._authorship_model = authorship_model
        self._model_settings = model_settings

    def generate_bundle(self, input: EngineeringTeamInput) -> EngineeringTeamOutput:
        output = self._engineering_agent_graph.run(input)
        bundle = output.game_bundle.model_copy(
            update={
                "hero_texture_url": input.hero_texture_url
                or output.game_bundle.hero_texture_url,
                "backdrop_texture_url": input.backdrop_texture_url
                or output.game_bundle.backdrop_texture_url,
                "hazard_texture_url": input.hazard_texture_url
                or output.game_bundle.hazard_texture_url,
                "platform_texture_url": input.platform_texture_url
                or output.game_bundle.platform_texture_url,
                "collectible_texture_url": input.collectible_texture_url
                or output.game_bundle.collectible_texture_url,
                "hero_display_w": input.hero_display_w,
                "hero_display_h": input.hero_display_h,
                "hazard_display_w": input.hazard_display_w,
                "hazard_display_h": input.hazard_display_h,
                "collectible_display_w": input.collectible_display_w,
                "collectible_display_h": input.collectible_display_h,
            }
        )
        bundle = with_compiled_entry(bundle)
        bundle = self._attach_sdk_experiment(input, bundle)
        return EngineeringTeamOutput(game_bundle=bundle)

    def _attach_sdk_experiment(
        self, input: EngineeringTeamInput, bundle: GameBundle
    ) -> GameBundle:
        if not self._lab.sdk_enabled:
            return bundle.model_copy(
                update={
                    "sdk_source": "",
                    "sdk_review_verdict": "skipped",
                    "sdk_review_notes": ["SDK experiment disabled (lab)"],
                    "sdk_authorship": "none",
                    "sdk_gameplay_notes": [],
                }
            )

        authorship = "template"
        gameplay_notes: list[str] = ["IR→SDK template"]
        use_llm_author = (
            self._lab.sdk_llm_authorship and self._authorship_model is not None
        )
        if use_llm_author:
            sdk_source, gameplay_notes, authorship = author_sdk_javascript_with_llm(
                input,
                bundle,
                model=self._authorship_model,
                model_settings=self._model_settings,
            )
        else:
            sdk_source = compile_sdk_source_from_bundle(bundle)
            if self._lab.sdk_llm_authorship and self._authorship_model is None:
                gameplay_notes = [
                    "LLM authorship requested but no model configured; used template"
                ]

        use_llm_review = (
            self._lab.sdk_llm_review and self._security_review_model is not None
        )
        if use_llm_review:
            review = review_sdk_javascript_with_llm(
                sdk_source,
                model=self._security_review_model,
                model_settings=self._model_settings,
            )
        else:
            review = review_sdk_javascript_static(sdk_source)
            if not self._lab.sdk_llm_review:
                review = review.model_copy(
                    update={
                        "notes": [
                            *review.notes,
                            "LLM security review skipped (lab)",
                        ]
                    }
                )

        # If authored JS is denied, keep IR Playable and fall back template for SDK.
        if review.verdict != "allow" and authorship == "llm":
            fallback = compile_sdk_source_from_bundle(bundle)
            fallback_review = review_sdk_javascript_static(fallback)
            if fallback_review.verdict == "allow":
                return bundle.model_copy(
                    update={
                        "sdk_source": fallback,
                        "sdk_review_verdict": fallback_review.verdict,
                        "sdk_review_notes": [
                            *review.notes,
                            "Authored SDK denied; fell back to IR template for Play",
                        ],
                        "sdk_authorship": "llm_fallback",
                        "sdk_gameplay_notes": [
                            *gameplay_notes,
                            "Security review denied authored JS",
                        ],
                    }
                )

        return bundle.model_copy(
            update={
                "sdk_source": sdk_source,
                "sdk_review_verdict": review.verdict,
                "sdk_review_notes": review.notes,
                "sdk_authorship": authorship,
                "sdk_gameplay_notes": gameplay_notes,
            }
        )

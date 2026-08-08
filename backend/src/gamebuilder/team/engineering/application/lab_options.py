"""TEMP: mutable Engineering experiment flags for local A/B testing.

Remove this module (and /api/lab/* + Lab UI) before any external release.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EngineeringLabOptions:
    """Process-wide lab toggles — changes apply to the next Engineering run / Play."""

    sdk_enabled: bool = True
    sdk_llm_review: bool = True
    # When True and an LLM is configured, author sdkSource via Cyborg.boot JS.
    sdk_llm_authorship: bool = True
    # When True, Play may load sdkSource even if review is not allow (unsafe).
    allow_unreviewed_sdk_play: bool = False
    preferred_play_runtime: str = "ir"  # ir | sdk — advisory for clients

    def snapshot(self) -> dict[str, bool | str]:
        return {
            "sdkEnabled": self.sdk_enabled,
            "sdkLlmReview": self.sdk_llm_review,
            "sdkLlmAuthorship": self.sdk_llm_authorship,
            "allowUnreviewedSdkPlay": self.allow_unreviewed_sdk_play,
            "preferredPlayRuntime": self.preferred_play_runtime,
        }

    def apply(
        self,
        *,
        sdk_enabled: bool | None = None,
        sdk_llm_review: bool | None = None,
        sdk_llm_authorship: bool | None = None,
        allow_unreviewed_sdk_play: bool | None = None,
        preferred_play_runtime: str | None = None,
    ) -> None:
        if sdk_enabled is not None:
            self.sdk_enabled = sdk_enabled
        if sdk_llm_review is not None:
            self.sdk_llm_review = sdk_llm_review
        if sdk_llm_authorship is not None:
            self.sdk_llm_authorship = sdk_llm_authorship
        if allow_unreviewed_sdk_play is not None:
            self.allow_unreviewed_sdk_play = allow_unreviewed_sdk_play
        if preferred_play_runtime is not None:
            runtime = preferred_play_runtime.strip().lower()
            if runtime not in {"ir", "sdk"}:
                raise ValueError("preferredPlayRuntime must be 'ir' or 'sdk'")
            self.preferred_play_runtime = runtime


# Default singleton used when wiring without an explicit instance.
DEFAULT_LAB_OPTIONS = EngineeringLabOptions()

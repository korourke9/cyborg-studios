"""LLM security review for SDK JavaScript before Play can execute it."""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_sync import run_agent_sync
from gamebuilder.team.engineering.application.sdk_lint import lint_sdk_javascript

_SYSTEM = (
    "You are a security reviewer for browser game JavaScript that will run inside "
    "a sandboxed iframe with a Cyborg Phaser SDK. "
    "Allow only code that implements a 2D game via Cyborg.boot. "
    "Deny anything that looks like data exfiltration, parent-frame access, "
    "network calls, storage access, eval, dynamic code loading, crypto mining, "
    "or attempts to escape the sandbox. "
    "Respond with JSON only matching the schema."
)


class SdkSecurityReview(BaseModel):
    verdict: str = Field(description="allow or deny")
    notes: list[str] = Field(default_factory=list)


def review_sdk_javascript_static(source: str) -> SdkSecurityReview:
    issues = lint_sdk_javascript(source)
    if issues:
        return SdkSecurityReview(verdict="deny", notes=issues)
    return SdkSecurityReview(verdict="allow", notes=["Static lint passed"])


def review_sdk_javascript_with_llm(
    source: str,
    *,
    model: Model,
    model_settings: ModelSettings | None = None,
) -> SdkSecurityReview:
    static = review_sdk_javascript_static(source)
    if static.verdict == "deny":
        return static

    agent: Agent[None, SdkSecurityReview] = Agent(
        model,
        output_type=SdkSecurityReview,
        system_prompt=_SYSTEM,
        model_settings=model_settings,
        retries=2,
    )
    result = run_agent_sync(
        agent,
        (
            "Review this SDK game script. Verdict must be allow or deny.\n\n"
            f"```javascript\n{source[:12000]}\n```"
        ),
    )
    verdict = result.verdict.strip().lower()
    if verdict not in {"allow", "deny"}:
        verdict = "deny"
        result.notes = [*result.notes, f"Invalid verdict coerced to deny: {result.verdict}"]
    return SdkSecurityReview(verdict=verdict, notes=result.notes)

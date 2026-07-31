from pydantic import ValidationError

from gamebuilder.orchestration.application.port.llm import LlmModel
from gamebuilder.team.design.application.design_contracts import (
    CRITIQUE_SYSTEM_PROMPT,
    DRAFT_SYSTEM_PROMPT,
    REVISE_SYSTEM_PROMPT,
    CritiqueResult,
    DesignArtifactBundle,
    critique_user_prompt,
    draft_user_prompt,
    revise_user_prompt,
)
from gamebuilder.team.design.domain.model import DesignTeamOutput

# Kept for the optional LlmModel-based reflective path (non-PydanticAI).
DESIGN_JSON_SCHEMA = """
Return a single JSON object with this exact shape (camelCase keys):
{
  "visionDoc": {
    "summary": string,
    "playerFantasy": string,
    "targetMood": string
  },
  "designPillars": {
    "pillars": [string, string, string]
  },
  "mechanicsSpec": {
    "movement": string,
    "coreLoop": string,
    "verbs": [string, ...]
  },
  "systemsSpec": {
    "progression": string,
    "challenge": string,
    "scoring": string
  }
}
""".strip()


class DesignReflectionProcess:
    """Framework-free draft → critique → revise → validate process over LlmModel."""

    def __init__(self, llm: LlmModel) -> None:
        self._llm = llm

    def draft(self, prompt: str) -> str:
        return self._llm.complete(
            system=f"{DRAFT_SYSTEM_PROMPT}\nRespond with JSON only.\n{DESIGN_JSON_SCHEMA}",
            user=draft_user_prompt(prompt),
        )

    def critique(self, prompt: str, draft_json: str) -> str:
        return self._llm.complete(
            system=(
                f"{CRITIQUE_SYSTEM_PROMPT} Respond with JSON only: "
                '{"issues":[string],"severity":[string],"suggestions":[string]}'
            ),
            user=critique_user_prompt(prompt, draft_json),
        )

    def revise(self, prompt: str, draft_json: str, critique_json: str) -> str:
        return self._llm.complete(
            system=f"{REVISE_SYSTEM_PROMPT}\nRespond with JSON only.\n{DESIGN_JSON_SCHEMA}",
            user=revise_user_prompt(prompt, draft_json, critique_json),
        )

    def validate(self, candidate_json: str, *, allow_repair: bool = True) -> DesignTeamOutput:
        try:
            return DesignArtifactBundle.model_validate_json(candidate_json).to_output()
        except ValidationError as exc:
            if not allow_repair:
                raise
            repaired = self._llm.complete(
                system=(
                    "Fix the following JSON so it matches the required design schema. "
                    f"Respond with JSON only.\n{DESIGN_JSON_SCHEMA}"
                ),
                user=f"Invalid JSON:\n{candidate_json}\n\nValidation error:\n{exc}",
            )
            return DesignArtifactBundle.model_validate_json(repaired).to_output()

    def run(self, prompt: str) -> DesignTeamOutput:
        draft_json = self.draft(prompt)
        critique_json = self.critique(prompt, draft_json)
        try:
            CritiqueResult.model_validate_json(critique_json)
        except ValidationError:
            pass
        revised_json = self.revise(prompt, draft_json, critique_json)
        return self.validate(revised_json, allow_repair=True)

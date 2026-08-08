from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from gamebuilder.orchestration.infrastructure.llm.pydantic_ai_sync import run_agent_sync
from gamebuilder.team.qa.application.qa_contracts import (
    CRITIQUE_SYSTEM_PROMPT,
    DRAFT_SYSTEM_PROMPT,
    REVISE_SYSTEM_PROMPT,
    CritiqueResult,
    QaArtifactBundle,
    critique_user_prompt,
    draft_user_prompt,
    revise_user_prompt,
)
from gamebuilder.team.qa.domain.model import QaTeamInput, QaTeamOutput

_DEFAULT_RETRIES = 3


class PydanticAIQaAgentGraph:
    def __init__(
        self,
        model: Model,
        *,
        critique_model: Model | None = None,
        revise_model: Model | None = None,
        model_settings: ModelSettings | None = None,
        retries: int = _DEFAULT_RETRIES,
    ) -> None:
        self._draft_agent: Agent[None, QaArtifactBundle] = Agent(
            model,
            output_type=QaArtifactBundle,
            system_prompt=DRAFT_SYSTEM_PROMPT,
            model_settings=model_settings,
            retries=retries,
        )
        self._critique_agent: Agent[None, CritiqueResult] = Agent(
            critique_model or model,
            output_type=CritiqueResult,
            system_prompt=CRITIQUE_SYSTEM_PROMPT,
            model_settings=model_settings,
            retries=retries,
        )
        self._revise_agent: Agent[None, QaArtifactBundle] = Agent(
            revise_model or model,
            output_type=QaArtifactBundle,
            system_prompt=REVISE_SYSTEM_PROMPT,
            model_settings=model_settings,
            retries=retries,
        )

    def run(self, input: QaTeamInput) -> QaTeamOutput:
        draft = run_agent_sync(self._draft_agent, draft_user_prompt(input))
        draft_json = draft.model_dump_json(by_alias=True)

        critique = run_agent_sync(
            self._critique_agent,
            critique_user_prompt(input, draft_json),
        )

        revised = run_agent_sync(
            self._revise_agent,
            revise_user_prompt(input, draft_json, critique.model_dump_json()),
        )

        return revised.to_output()

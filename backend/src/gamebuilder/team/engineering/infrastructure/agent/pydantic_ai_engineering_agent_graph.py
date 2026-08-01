from pydantic_ai import Agent
from pydantic_ai.models import Model

from gamebuilder.team.engineering.application.engineering_contracts import (
    CRITIQUE_SYSTEM_PROMPT,
    DRAFT_SYSTEM_PROMPT,
    REVISE_SYSTEM_PROMPT,
    CritiqueResult,
    EngineeringLevelDraft,
    critique_user_prompt,
    draft_user_prompt,
    revise_user_prompt,
)
from gamebuilder.team.engineering.domain.model import (
    EngineeringTeamInput,
    EngineeringTeamOutput,
)


class PydanticAIEngineeringAgentGraph:
    """EngineeringAgentGraph backed by PydanticAI structured level drafts."""

    def __init__(
        self,
        model: Model,
        *,
        critique_model: Model | None = None,
        revise_model: Model | None = None,
    ) -> None:
        self._draft_agent: Agent[None, EngineeringLevelDraft] = Agent(
            model,
            output_type=EngineeringLevelDraft,
            system_prompt=DRAFT_SYSTEM_PROMPT,
        )
        self._critique_agent: Agent[None, CritiqueResult] = Agent(
            critique_model or model,
            output_type=CritiqueResult,
            system_prompt=CRITIQUE_SYSTEM_PROMPT,
        )
        self._revise_agent: Agent[None, EngineeringLevelDraft] = Agent(
            revise_model or model,
            output_type=EngineeringLevelDraft,
            system_prompt=REVISE_SYSTEM_PROMPT,
        )

    def run(self, input: EngineeringTeamInput) -> EngineeringTeamOutput:
        draft = self._draft_agent.run_sync(draft_user_prompt(input)).output
        draft_json = draft.model_dump_json(by_alias=True)

        critique = self._critique_agent.run_sync(
            critique_user_prompt(input, draft_json)
        ).output

        revised = self._revise_agent.run_sync(
            revise_user_prompt(input, draft_json, critique.model_dump_json())
        ).output

        return revised.to_output()

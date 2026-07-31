from pydantic_ai import Agent
from pydantic_ai.models import Model

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
from gamebuilder.team.design.domain.model import DesignTeamInput, DesignTeamOutput


class PydanticAIDesignAgentGraph:
    """DesignAgentGraph backed by PydanticAI agents with structured outputs.

    Reflection loop stays draft → critique → revise; PydanticAI owns model I/O
    and schema validation. Prompt text lives in application contracts.
    """

    def __init__(
        self,
        model: Model,
        *,
        critique_model: Model | None = None,
        revise_model: Model | None = None,
    ) -> None:
        self._draft_agent: Agent[None, DesignArtifactBundle] = Agent(
            model,
            output_type=DesignArtifactBundle,
            system_prompt=DRAFT_SYSTEM_PROMPT,
        )
        self._critique_agent: Agent[None, CritiqueResult] = Agent(
            critique_model or model,
            output_type=CritiqueResult,
            system_prompt=CRITIQUE_SYSTEM_PROMPT,
        )
        self._revise_agent: Agent[None, DesignArtifactBundle] = Agent(
            revise_model or model,
            output_type=DesignArtifactBundle,
            system_prompt=REVISE_SYSTEM_PROMPT,
        )

    def run(self, input: DesignTeamInput) -> DesignTeamOutput:
        draft = self._draft_agent.run_sync(draft_user_prompt(input.prompt)).output
        draft_json = draft.model_dump_json(by_alias=True)

        critique = self._critique_agent.run_sync(
            critique_user_prompt(input.prompt, draft_json)
        ).output

        revised = self._revise_agent.run_sync(
            revise_user_prompt(
                input.prompt,
                draft_json,
                critique.model_dump_json(),
            )
        ).output

        return revised.to_output()

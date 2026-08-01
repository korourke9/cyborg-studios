from gamebuilder.team.story.domain.model import (
    ExperienceMilestones,
    NarrativeSpec,
    StoryTeamInput,
    StoryTeamOutput,
)


class DeterministicStoryAgentGraph:
    def run(self, input: StoryTeamInput) -> StoryTeamOutput:
        twist = input.prompt.strip() or "the player's adventure"
        return StoryTeamOutput(
            narrative_spec=NarrativeSpec(
                premise=(
                    f"A short platformer tale spun from “{twist}”, guided by "
                    f"{input.vision_summary or 'a clear playful vision'}."
                ),
                tone="Warm, curious, and lightly heroic.",
                protagonist=(
                    "A small explorer who learns the world's one memorable trick "
                    f"while chasing {input.player_fantasy or 'confident movement'}."
                ),
                setting=(
                    "Compact stages that echo the prompt, with safe teaching rooms "
                    "before tighter challenges."
                ),
            ),
            experience_milestones=ExperienceMilestones(
                milestones=[
                    "Arrive somewhere strange and learn the basic jump.",
                    "Meet the prompt's twist in a safe tutorial pocket.",
                    "Cross a denser hazard stretch using that twist.",
                    "Reach a short finale that rewards mastery and collectibles.",
                ]
            ),
        )

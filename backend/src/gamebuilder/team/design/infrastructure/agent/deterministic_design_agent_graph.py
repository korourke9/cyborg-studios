from gamebuilder.team.design.domain.model import (
    DesignPillars,
    DesignTeamInput,
    DesignTeamOutput,
    MechanicsSpec,
    SystemsSpec,
    VisionDoc,
)


class DeterministicDesignAgentGraph:
    def run(self, input: DesignTeamInput) -> DesignTeamOutput:
        return DesignTeamOutput(
            vision_doc=VisionDoc(
                summary=f"A focused 2D platformer concept generated from: {input.prompt}",
                player_fantasy=(
                    "Move with confidence through playful spaces that transform "
                    "the prompt into readable action."
                ),
                target_mood="Whimsical, energetic, and immediately playable.",
            ),
            design_pillars=DesignPillars(
                pillars=[
                    "Readable movement before complexity",
                    "One memorable twist from the prompt",
                    "Short levels with fast restarts",
                ]
            ),
            mechanics_spec=MechanicsSpec(
                movement="Run, jump, and air-control tuned for forgiving platforming.",
                core_loop=(
                    "Explore a compact level, master the prompt-inspired obstacle, "
                    "collect rewards, and reach the exit."
                ),
                verbs=["run", "jump", "collect", "avoid", "finish"],
            ),
            systems_spec=SystemsSpec(
                progression=(
                    "Start with simple jumps, then introduce one prompt-inspired "
                    "mechanic in a safe tutorial space."
                ),
                challenge=(
                    "Hazards and gaps escalate in density while keeping checkpoints close."
                ),
                scoring="Reward completion time, collectibles, and damage-free play.",
            ),
        )

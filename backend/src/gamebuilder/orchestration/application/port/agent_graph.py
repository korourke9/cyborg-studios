from typing import Protocol, TypeVar

I = TypeVar("I", contravariant=True)
O = TypeVar("O", covariant=True)


class AgentGraph(Protocol[I, O]):
    def run(self, input: I) -> O:
        """Execute a bounded team reasoning graph."""

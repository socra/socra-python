import typing

from socra.agents.agent_decision import decide
from socra.schemas import Schema
from socra.agents.context import Context


class Agent(Schema):
    key: str
    name: str
    description: str
    children: typing.List["Agent"] = []
    runs: typing.Optional[typing.Callable[[Context], None]] = None

    def __eq__(self, other: "Agent") -> bool:
        return self.key == other.key

    def add_child(self, child: "Agent"):
        if self.runs is not None:
            raise ValueError("Cannot add children to an agent with a run method")

        self.children.append(child)

    def run(self, context: Context):
        """
        Run the agent based on the context provided.
        If the agent has children, we'll run an action to decide
        which child to call based on the context provided.

        If the agent has no children, `runs` will be called.
        """

        context.add_invocation(self.key)

        # agent has children, we'll run an action to decide
        # which child to call based on the context provided.
        if len(self.children) > 0:
            child_to_call = decide(self, context)
            child_to_call.run(context)
        elif self.runs:
            self.runs(context)
        else:
            raise ValueError(f"Agent {self.key} has no children and no run method")

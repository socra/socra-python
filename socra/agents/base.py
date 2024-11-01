import typing

from socra.agents.agent_decision import decide
from socra.schemas import Schema
from socra.agents.context import Context
from socra.messages import Message


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

        max_retries = 3

        context.add_invocation(self.key)

        # agent has children, we'll run an action to decide
        # which child to call based on the context provided.
        if len(self.children) > 0:
            child_to_call = decide(self, context)

            child_to_call.run(context)

            # current_attempts = 0
            # while current_attempts < max_retries:
            #     # try:
            #         child_to_call.run(context)
            #         break
            #     except Exception as e:
            #         current_attempts += 1
            #         context.add_message(
            #             Message(
            #                 role=Message.Role.ASSISTANT,
            #                 content=f"Error running {child_to_call.key}: {e}",
            #             )
            #         )
            #         child_to_call = decide(self, context)

        elif self.runs:
            self.runs(context)
        else:
            raise ValueError(f"Agent {self.key} has no children and no run method")

import typing
from socra.agents.base import Agent

from socra.agents.user_interaction.actions import (
    input_choices,
    terminate_program,
    text_input,
)


class UserInteractionAgent(Agent):
    key: str = "user_interaction"
    name: str = "interact with user"
    description: str = "Interact with user to get input or provide output."

    children: typing.List[Agent] = [
        Agent(
            key="input_choices",
            name="Input Choices",
            description="Ask user to choose from a list of options.",
            runs=input_choices,
        ),
        Agent(
            key="text_input",
            name="Text Input",
            description="Ask user to input text.",
            runs=text_input,
        ),
        Agent(
            key="sig_int",
            name="Terminate",
            description="Terminate the program. You must be sure there is nothing else to do. Always confirm with user before calling this.",
            runs=terminate_program,
        ),
    ]

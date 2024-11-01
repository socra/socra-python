import typing

from pydantic import ConfigDict
from socra.completions.base import TokenCost
from socra.messages.base import Message
from socra.schemas import Schema
from socra.completions.base import Completion
from socra.utils.spinner import Spinner


class Context(Schema):
    """
    Core context object passed around and manipulated by agents
    """

    messages: typing.List[Message] = []

    # history of action invocations
    history: typing.List[str] = []

    token_cost: TokenCost = TokenCost(
        input=0,
        output=0,
        total=0,
    )

    completions: typing.List[Completion] = []

    # allow arbitrary types
    model_config: ConfigDict = {
        "arbitrary_types_allowed": True,
    }

    spinner: typing.Optional[Spinner] = Spinner()

    def start_thinking(self, message: str):
        """
        Utility message to help
        """
        self.spinner.message = message
        self.spinner.start()

    def stop_thinking(self, thought: str):
        self.add_thought(thought)
        self.spinner.message = thought
        self.spinner.finish()
        self.spinner.reset()

    def track_completion(self, completion: Completion):
        """
        Tracks a completion in the execution context
        """
        self.completions.append(completion)
        self.token_cost += completion.response.cost

    def add_invocation(self, key: str):
        self.history.append(key)

    def add_thought(self, thought: str):
        self.messages.append(Message(role=Message.Role.ASSISTANT, content=thought))

    def add_message(self, message: Message):
        self.messages.append(message)

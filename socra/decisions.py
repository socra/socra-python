import typing
from socra.completions.usage import TokenCost
from socra.context import Context
from socra.schemas import Schema
from socra.messages import Message
from socra.models import Model
from socra.prompts import Prompt
from socra.completions import Completion, ChunkPayload, MockResponse
import json


class Option(Schema):
    """
    An option is a choice that can be made in a decision.
    """

    key: str
    """
    A unique key for the option. This key is used to identify the option.
    """

    name: str
    """
    A human-readable name for the option.
    """

    description: str
    """
    A human-readable description of the option.
    """

    def __eq__(self, other: "Option") -> bool:
        if not isinstance(other, Option):
            return False
        return self.key == other.key

    def to_str(self) -> str:
        return _option_str.format(
            key=self.key,
            name=self.name,
            description=self.description,
        ).strip()


_option_str = """
- key: {key}
  name: {name}
  description: {description}
"""


class DecisionConfig(Schema):
    on_chunk: typing.Optional[typing.Callable[[ChunkPayload], None]] = None
    """
    Optional callable that will be called with the chunk payload as it is received.
    """

    mock_response: typing.Optional[MockResponse] = None


class Decision(Schema):
    """
    Core Decision object, representing a decision made by an agent.

    Call Decision.make() to make a decision based on context and options.
    Resulting decision will contain the chosen option and reasoning.
    """

    option: Option
    """
    The chosen option.
    """

    reasoning: str
    """
    The reasoning behind the decision.
    """

    token_cost: TokenCost

    @classmethod
    def make(
        cls,
        context: Context,
        options: typing.List[Option],
        config: typing.Optional[DecisionConfig] = None,
    ) -> "Decision":
        """
        Make a decision based on the context and options.
        """

        return make_decision(context, options, config)


def make_decision(
    context: Context,
    options: typing.List[Option],
    config: typing.Optional[DecisionConfig] = None,
) -> Decision:
    """
    A decision requires context and options.
    """

    options_str = "\n".join([option.to_str() for option in options])

    completion = Completion(
        model=Model.for_key(Model.Key.GPT_4O_MINI_2024_07_18),
        prompt=Prompt(
            messages=[
                *context.messages,
                Message(
                    role=Message.Role.HUMAN,
                    content=_decision_prompt.format(options=options_str),
                ),
            ]
        ),
        on_chunk=config.on_chunk if config and config.on_chunk else None,
        mock_response=config.mock_response if config and config.mock_response else None,
    )
    resp = completion.process()
    print("prompt")
    print(completion.prompt)

    content = resp.content
    dct = json.loads(content)
    if "key" not in dct:
        raise ValueError("Missing 'key' in response")
    if "reasoning" not in dct:
        raise ValueError("Missing 'reasoning' in response")

    selected_key = dct["key"]
    reasoning = dct["reasoning"]

    # find
    selected_option = next(
        (option for option in options if option.key == selected_key), None
    )

    if not selected_option:
        raise ValueError(f"Option with key '{selected_key}' not found")

    decision = Decision(
        option=selected_option,
        reasoning=reasoning,
        token_cost=completion.response.cost,
    )

    return decision


_decision_prompt = """Based on the context above, which option should be chosen?

Your response must be in JSON format, and should include the key of the action to take.

Available actions:
{options}

JSON response format:
- key: The key of the action to take
- reasoning: Extremely brief thought on why the action was chosen

Example:
{{
    "key": "...",
    "reasoning": "the action..."
}}

Respond only in JSON format.
"""


class ActionResult(Schema):
    pass


class Action(Option):
    """
    Actions are either executable or have nested options.
    """

    runs: typing.Optional[typing.Callable[[Context], None]] = None
    """
    Callable that will be run when the option is chosen.
    """

    children: typing.Optional[typing.List["Action"]] = []
    """
    Nested actions.
    """

    def run(self, context: Context) -> ActionResult:
        """
        Actions take context as input and either:
        - run a callable, or
        - choose a nested action to run and invoke it.
        """

        if self.runs is not None:
            return self.runs(context)

        decision = Decision.make(context, self.children)
        return decision.option.run(context)

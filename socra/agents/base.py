import typing

from socra.schemas import Schema
from socra.prompts import Prompt
from socra.messages import Message
from socra.completions import Completion
from socra.models import Model
import json

from socra.utils.decorators import throttle
from socra.utils.spinner import Spinner
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

        context.add_invocation(self.key)

        # agent has children, we'll run an action to decide
        # which child to call based on the context provided.
        if len(self.children) > 0:
            child_to_call = self.decide(context)
            child_to_call.run(context)
        elif self.runs:
            self.runs(context)
        else:
            raise ValueError(f"Agent {self.key} has no children and no run method")

    def as_decision_str(self) -> str:
        """
        Output the agent as a decision list item.
        """
        prompt = _as_decision_prompt.format(
            key=self.key, name=self.name, description=self.description
        )

        # strip leading and trailing whitespace
        return prompt.strip()

    def decide(self, context: Context) -> "Agent":
        """
        Use LLM to decide on which child to call based on the context provided.
        """

        children_items = [child.as_decision_str() for child in self.children]
        children_str = "\n".join(children_items)
        prompt = Prompt(
            messages=[
                *context.messages,
                Message(
                    role=Message.Role.HUMAN,
                    content=_decision_prompt.format(children=children_str),
                ),
            ]
        )
        model = Model.for_key(Model.Key.GPT_4O_MINI_2024_07_18)
        spinner = Spinner(message=f"Making decision for {self.name}")

        @throttle(0.1)
        def on_chunk(chunk):
            spinner.spin()

        cr = Completion(
            model,
            prompt,
            # mock_response=inputs.mock_response,
            on_chunk=on_chunk,
        )
        resp = cr.process()
        context.track_completion(cr)

        content = resp.content
        dct = json.loads(content)
        if "key" not in dct:
            raise ValueError("Missing 'key' in response")
        if "reasoning" not in dct:
            raise ValueError("Missing 'reasoning' in response")

        selected_key = dct["key"]
        reasoning = dct["reasoning"]

        # find the child with the selected key
        selected_child = None
        for child in self.children:
            if child.key == selected_key:
                selected_child = child
                break

        if not selected_child:
            raise ValueError(f"Child with key '{selected_key}' not found")

        # finally, update spinner with decision and finish
        thought = f"Decided to {selected_child.name} because {reasoning}"
        spinner.message = thought
        spinner.finish()

        context.add_thought(thought)

        return selected_child


_as_decision_prompt = """
- key: {key}
  name: {name}
  description: {description}
"""

_decision_prompt = """Based on the context above, which action should be taken?

Your response must be in JSON format, and should include the key of the action to take.

Available actions:
{children}

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

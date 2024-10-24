import typing
import socra
from enum import Enum
import json

from socra.utils.decorators import throttle
from socra.utils.spinner import Spinner


class Inputs(socra.Schema):
    node: socra.Node
    prompt: str


class ActionKey(Enum):
    DO_NOTHING = "do_nothing"
    ADD_CHILD = "add_child"
    RENAME = "rename"
    UPDATE_CONTENT = "update_content"


class EnabledAction(socra.Schema):
    key: ActionKey
    name: str
    description: str
    # action: socra.Action


class Outputs(socra.Schema):
    key: ActionKey
    reason: str


class NodeRootAction(socra.Action[Inputs, None]):
    """
    For a given node, the root action decides what action to take,
    based on the node and prompt given.
    """

    Inputs: typing.ClassVar = Inputs
    Output: typing.ClassVar = None

    def run(self, inputs):
        node = inputs.node

        actions: typing.List[EnabledAction] = [
            EnabledAction(
                key=ActionKey.DO_NOTHING,
                name="Do Nothing",
                description="Do nothing. No action is needed.",
            )
        ]
        if node.type == socra.Node.Type.FILE:
            actions.append(
                EnabledAction(
                    key=ActionKey.UPDATE_CONTENT,
                    name="Update Content",
                    description="Update the content of the file. Only call this if the file content needs to change in some important way.",
                )
            )
            content = node.content
        else:
            actions.append(
                EnabledAction(
                    key=ActionKey.ADD_CHILD,
                    name="Add Child",
                    description="Add a child node to this directory. Can be a file or a directory.",
                )
            )
            children_str = "\n".join(
                [f"- {child.name}" for child in node.get_children()]
            )
            content = (
                f"Name: {node.name}\nType: {node.type.value}\nChildren: {children_str}"
            )

        actions_str = "\n".join(
            [
                f"- key: {action.key.value}\n  description: {action.description}"
                for action in actions
            ]
        )

        model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
        prompt = socra.Prompt(
            messages=[
                socra.Message(
                    role=socra.Message.Role.SYSTEM,
                    content=instructions.format(
                        prompt=inputs.prompt,
                        node=node,
                        actions=actions_str,
                    ),
                ),
                socra.Message(role=socra.Message.Role.HUMAN, content=content),
            ]
        )

        spinner = Spinner(message=f"Deciding whether to update {node.path}")

        @throttle(0.1)
        def on_chunk(chunk):
            spinner.spin()

        cr = socra.Completion(
            model,
            prompt,
            # mock_response=inputs.mock_response,
            on_chunk=on_chunk,
        )
        resp = cr.process()

        content = resp.content

        # parse JSON response
        dct = json.loads(content)
        outputs = Outputs(
            key=ActionKey(dct["key"]),
            reason=dct["reason"],
        )

        spinner.message = (
            f"Decided to {outputs.key.value} because {outputs.reason.lower()}"
        )

        spinner.finish()

        return outputs


instructions = """You are an expert decision maker.

I will provide you with a {node.type}, and your task is to decide what action should be taken.

Based on the following prompt, what action should be taken on the {node.type}?
<prompt>
{prompt}
</prompt>


Your response should be in JSON format, with the key being one of the following:

Actions:
{actions}

Example JSON response:
{{
    "key": "do_nothing",
    "reason": "the file is already up to date"
}}


Respond ONLY with the JSON structure above.
"""

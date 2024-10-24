import socra
import json
from socra.nodes.node import NodeType
from socra.utils.decorators import throttle
from socra.utils.spinner import Spinner
import typing


from socra.nodes import Node


class Inputs(socra.Schema):
    node: Node
    prompt: str


class Outputs(socra.Schema):
    name: str
    type: NodeType
    reason: str


class NodeAddChild(socra.Action[Inputs, str]):
    """
    Node content update action.
    """

    Inputs: typing.ClassVar = Inputs

    def run(self, inputs):
        model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)

        prompt = socra.Prompt(
            messages=[
                socra.Message(
                    role=socra.Message.Role.HUMAN,
                    content=instructions.format(
                        prompt=inputs.prompt,
                        current_directory=inputs.node.name,
                        child_items="\n".join(
                            [f"- {child.name}" for child in inputs.node.get_children()]
                        ),
                    ),
                ),
            ]
        )
        spinner = Spinner(message=f"Adding a new node to {inputs.node.path}")

        @throttle(0.1)
        def on_chunk(stream_chunk):
            spinner.spin()

        cr = socra.Completion(
            model,
            prompt,
            # mock_response=inputs.mock_response,
            on_chunk=on_chunk,
        )
        resp = cr.process()

        spinner.finish()
        content = resp.content

        if content.startswith("```"):
            # remove first and last line
            content = "\n".join(content.split("\n")[1:-1])

        # parse JSON response
        dct = json.loads(content)
        outputs = Outputs(
            name=dct["name"],
            type=NodeType(dct["type"]),
            reason=dct["reason"],
        )

        spinner.message = f"Decided to add {outputs.name} of type {outputs.type} because {outputs.reason.lower()}"

        return outputs


instructions = """You are an expert developer.

Given some information about the current directory and its current contents, you will respond in JSON format with the name of a new file or directory to create.

The new item must not exist in the current directory.

The information is as follows:
New item instructions: "{prompt}"
Current directory name: "{current_directory}"
Child items:
{child_items}


Your response should be in the following JSON format with the following keys:
- "name": the name of the new item to create
- "type": the type of the new item to create, either "file" or "directory"
- "reason": the reason for the name

For example:
{{
    "name": "new_file.py",
    "type": "file",
    "reason": "I chose this name because..."
}}

Another example: 
{{
    "name": "new_directory",
    "type": "directory",
    "reason": "I chose this name because..."
}}

Respond ONLY with the JSON structure above.
"""

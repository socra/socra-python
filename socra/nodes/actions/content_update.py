import socra
from socra.utils.decorators import throttle
from socra.utils.spinner import Spinner
import typing


from socra.nodes import Node


class Inputs(socra.Schema):
    node: Node
    prompt: str


class NodeContentUpdate(socra.Action[Inputs, str]):
    """
    Node content update action.
    """

    Inputs: typing.ClassVar = Inputs

    def run(self, inputs):
        if inputs.node.type != Node.Type.FILE:
            raise ValueError("Node must be a file.")

        model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)

        prompt = socra.Prompt(
            messages=[
                socra.Message(
                    role=socra.Message.Role.SYSTEM,
                    content=system_prompt.format(prompt=inputs.prompt),
                ),
                socra.Message(
                    role=socra.Message.Role.HUMAN, content=inputs.node.content
                ),
            ]
        )
        spinner = Spinner(message=f"Improving {inputs.node.path}")

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

        return content


system_prompt = """You are an expert code improver.
Given some code, you will improve it with the following prompt:
"{prompt}"

Return only the improved code and nothing else.
"""

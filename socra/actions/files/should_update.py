import os
import socra
from socra.io.files import read_file, write_file
from socra.utils.decorators import throttle
from socra.utils.spinner import Spinner
import typing
import json


class Inputs(socra.Schema):
    target: str
    prompt: str = None


class Outputs(socra.Schema):
    should_update: bool
    reason: str


class ActionShouldUpdateFile(socra.Action[Inputs, Outputs]):
    Inputs: typing.ClassVar = Inputs
    Outputs: typing.ClassVar = Outputs

    def run(self, inputs) -> "Outputs":
        if not os.path.exists(inputs.target):
            raise FileNotFoundError(f"Target '{inputs.target}' not found.")

        # make sure target is a file (for now)
        if not os.path.isfile(inputs.target):
            raise ValueError(f"Target '{inputs.target}' must be a file.")

        file_contents = read_file(inputs.target)

        model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
        prompt = socra.Prompt(
            messages=[
                socra.Message(
                    role=socra.Message.Role.SYSTEM,
                    content=system_prompt.format(prompt=inputs.prompt),
                ),
                socra.Message(role=socra.Message.Role.HUMAN, content=file_contents),
            ]
        )

        spinner = Spinner(message=f"Deciding whether to update {inputs.target}")

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
        outputs = Outputs(**dct)

        if outputs.should_update:
            spinner.message = (
                f"Decided to update {inputs.target} because {outputs.reason.lower()}"
            )
        else:
            spinner.message = f"Decided not to update {inputs.target} because {outputs.reason.lower()}"

        spinner.finish()

        return outputs


system_prompt = """You are an expert decision maker.

Based on the following prompt, should the file be updated?
"{prompt}"


Your response should be in JSON format with the following structure:
If you believe the file should be updated:
{{
    "should_update": true,
    "reason": "the file..."
}}

If you believe the file should not be updated:
{{
    "should_update": false,
    "reason": "the file..."
}}

Respond ONLY with the JSON structure above.
"""

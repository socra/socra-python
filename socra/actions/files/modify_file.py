import os
import socra
from socra.io.files import read_file, write_file
from socra.utils.decorators import throttle
from socra.utils.spinner import Spinner
import typing


class Inputs(socra.Schema):
    target: str
    prompt: str = None


class ActionImproveFile(socra.Action[Inputs, None]):
    Inputs: typing.ClassVar = Inputs

    def run(self, inputs):
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

        spinner = Spinner(message=f"Improving {inputs.target}")

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

        write_file(inputs.target, content)


system_prompt = """You are an expert code improver.
Given some code, you will improve it with the following prompt:
"{prompt}"

Return only the improved code and nothing else.
"""

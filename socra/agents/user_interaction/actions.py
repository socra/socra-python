from socra.agents.context import Context
import os
import typing

from socra.parsers import parse_json
import socra
from socra.utils.decorators import throttle
from socra.schemas import Schema
import inquirer


def input_choices(context: Context):
    """
    Ask the user a question and provide a list of choices.
    """

    payload = get_input_choices_payload(context)

    context.start_thinking(f"Prompting user with: {payload.message}")

    if payload.allow_multiple:
        questions = [
            inquirer.Checkbox(
                "choices",
                message=payload.message,
                choices=payload.choices,
            ),
        ]
    else:
        questions = [
            inquirer.List(
                "choices",
                message=payload.message,
                choices=payload.choices,
            ),
        ]

    answers = inquirer.prompt(questions)

    context.stop_thinking(f"User selected: {answers['choices']} from {payload.choices}")


class InputChoicesPayload(Schema):
    message: str
    choices: typing.List[str]
    allow_multiple: bool = False


def get_input_choices_payload(context: Context) -> InputChoicesPayload:

    prompt = socra.Prompt(
        messages=[
            *context.messages,
            socra.Message(
                role=socra.Message.Role.HUMAN,
                content=get_input_choices_payload_prompt,
            ),
        ]
    )
    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
    context.start_thinking("Creating choices")

    @throttle(0.1)
    def on_chunk(chunk):
        context.spinner.spin()

    cr = socra.Completion(
        model,
        prompt,
        # mock_response=inputs.mock_response,
        on_chunk=on_chunk,
    )
    resp = cr.process()
    context.track_completion(cr)

    content = resp.content
    dct = parse_json(content)
    if "message" not in dct:
        raise ValueError("Missing 'message' in response")
    if "choices" not in dct:
        raise ValueError("Missing 'choices' in response")
    if "allow_multiple" not in dct:
        raise ValueError("Missing 'allow_multiple' in response")

    payload = InputChoicesPayload(
        message=dct["message"],
        choices=dct["choices"],
        allow_multiple=dct["allow_multiple"],
    )

    # context.stop_thinking(f"Gathered choices: {payload.choices}")

    return payload


get_input_choices_payload_prompt = """Based on the context above, create a multiple choice prompt for the user.

Your response must be in JSON format, and must include the following keys:
- message (str): The message to display to the user
- choices: (List[str]): A list of choices for the user to select from
- allow_multiple (bool): Whether the user can select multiple choices

Example:
{{
    "message": "...",
    "choices": ["...", "..."],
    "allow_multiple": true
}}

Respond only in JSON format.
"""


def text_input(context: Context):
    """
    Get text input from user.
    """

    # first, determine what we want to prompt the user
    payload = determine_user_input_prefix(context)

    # next, get input from the user
    context.add_thought(f"Getting input from user because: {payload.reasoning}")
    context.add_thought(payload.reasoning)
    # context.start_thinking(f"Getting input from user because: {payload.reasoning}")
    # context.stop_thinking(f"Finished getting input from user: {payload.message}")

    questions = [
        inquirer.Text("input", message=payload.prompt),
    ]
    answers = inquirer.prompt(questions)
    resp = answers["input"]
    context.add_message(socra.Message(role=socra.Message.Role.HUMAN, content=resp))


class UserInputPayload(Schema):
    prompt: str
    reasoning: str


def determine_user_input_prefix(context: Context) -> UserInputPayload:
    """
    Determine the user input prefix prompt.
    """
    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)

    @throttle(0.1)
    def on_chunk(chunk):
        context.spinner.spin()

    cr = socra.Completion(
        model,
        socra.Prompt(
            messages=[
                *context.messages,
                socra.Message(
                    role=socra.Message.Role.HUMAN,
                    content=determine_user_input_prefix_prompt,
                ),
            ]
        ),
        on_chunk=on_chunk,
    )
    resp = cr.process()
    context.track_completion(cr)

    content = resp.content
    dct = parse_json(content)
    if "prompt" not in dct:
        raise ValueError("Missing 'prompt' in response")

    payload = UserInputPayload(**dct)
    return payload


determine_user_input_prefix_prompt = """Based on the context above, what information do you need from the user?

The message will be used as a prefix to the user input (e.g. 'Please provide the file path: ').

Your response must be in JSON format, and should include the following keys:
- prompt: A brief message indicating what information you need from the user.

Example:
{{
    "prompt": "...",
    "reasoning": "the content..."
}}

Respond only in JSON format.
"""


def terminate_program(context: Context):

    context.stop()

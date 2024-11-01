import click
from pydantic import ConfigDict

from socra.agents.file_system.actions import create_file, update_file
from socra.agents.file_system.agent import FileSystemAgent
from socra.commands.describe import Describe

from dotenv import load_dotenv
from socra.completions.base import TokenCost
from socra.io.files import read_file, write_file
from socra.nodes import Node
from socra.nodes.actions.add_child import NodeAddChild
from socra.nodes.actions.content_update import NodeContentUpdate
from socra.nodes.actions.root import ActionKey, NodeRootAction
from socra.schemas.base import Schema
from socra.messages import Message
import socra
from socra.utils.decorators import throttle
from socra.utils.spinner import Spinner
import json
import os

from socra.agents import Agent, Context


def load_env():
    load_dotenv()


load_env()


@click.group()
def cli():
    """socra CLI tool for code improvement and description."""
    pass


@cli.command()
@click.argument("target", type=click.Path(exists=True))
@click.argument("prompt", type=click.STRING, required=False)
def improve(target: str, prompt: str):
    """Improve the specified file or directory."""

    a = NodeRootAction()
    node = Node.for_path(target)

    output = a.run(a.Inputs(node=node, prompt=prompt))

    if output.key == ActionKey.UPDATE_CONTENT:
        content = NodeContentUpdate().run(
            NodeContentUpdate.Inputs(node=Node.for_path(target), prompt=prompt)
        )
        node.content = content
        node.save()
    elif output.key == ActionKey.ADD_CHILD:
        out = NodeAddChild().run(NodeAddChild.Inputs(node=node, prompt=prompt))
        node.add_child(name=out.name, type=out.type)


@cli.command()
@click.argument("target", type=click.Path(exists=True))
@click.argument("prompt", type=click.STRING, required=False)
def describe(target: str, prompt: str):
    """Describe the specified file or directory."""
    print("adding describe")

    command = Describe(config=Describe.Config(target=target, prompt=prompt))
    command.execute()


@cli.command()
# add optional argument that allows for user to type anything
@click.argument("args", nargs=-1)  # This allows for any number of additional arguments
def dev(args):

    prompt = " ".join(args)

    agent = Agent(
        key="software_developer",
        name="Software Developer Agent",
        description="An agent that can develop software on the local file system. Especially good with file manipulation.",
        children=[
            Agent(
                key="await_user_input",
                name="Await User Input",
                description="Await user input from the console before continuing. Useful when you need to ask a question or gather more information from the user.",
                runs=await_user_input,
            ),
            FileSystemAgent(),
            Agent(
                key="finish",
                name="Finish",
                description="All done. Task accomplished. Should be called when no further action is needed.",
                runs=do_nothing,
            ),
            Agent(
                key="respond",
                name="Respond",
                description="Respond to the user with a message. Useful for providing a resolution or an update.",
                runs=respond,
            ),
        ],
    )

    ctx = Context()
    if prompt:
        ctx.add_message(Message(role=Message.Role.HUMAN, content=prompt))

    idx = 0
    while idx < 20:
        idx += 1
        agent.run(ctx)

        # if last invocation was do_nothing, break
        # if ctx.history[-1] == "finish":
        #     ctx.spinner.message = "All done"
        #     ctx.spinner.finish()
        #     break

    print("Cost")
    print("Num completions:", len(ctx.completions))
    print(ctx.token_cost)


def await_user_input(context: Context):

    input_str = determine_user_input_prefix(context)

    res = input(f"{input_str}: ")
    context.add_message(Message(role=Message.Role.HUMAN, content=res))


def determine_user_input_prefix(context: Context) -> str:
    """
    Determine the user input prefix prompt.
    """
    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
    spinner = Spinner(message="Determining user input prefix")

    @throttle(0.1)
    def on_chunk(chunk):
        spinner.spin()

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

    prompt = dct["prompt"]
    thought = f"Determined user input prefix: {prompt}"
    spinner.message = thought
    spinner.finish()
    context.add_thought(thought)
    return prompt


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


def do_nothing(context: Context):
    context.stop_thinking(
        "Finished the task. Should ask the user if they need anything else."
    )


def respond(context: Context):
    """
    Respond to the user with a message.
    """
    prompt = socra.Prompt(
        messages=[
            *context.messages,
            socra.Message(
                role=socra.Message.Role.HUMAN,
                content=respond_prompt,
            ),
        ]
    )
    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
    spinner = Spinner(message="Responding to the user")

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
    context.track_completion(cr)

    content = resp.content
    dct = parse_json(content)
    if "response" not in dct:
        raise ValueError("Missing 'response' in response")

    response = dct["response"]
    thought = f"Responded to the user: {response}"
    spinner.message = thought
    spinner.finish()
    context.add_thought(thought)


respond_prompt = """Based on the context above, respond to the user with a message.

Your response must be in JSON format, and should include the following keys:
- response: The message to respond with

Example:
{{
    "response": "..."
}}

Respond only in JSON format.
"""


def parse_json(json_str: str) -> dict:

    # if begins with ```, strip first line
    if json_str.startswith("```"):
        json_str = json_str.split("\n", 1)[1]

    # if ends with ```, strip last line
    if json_str.endswith("```"):
        json_str = json_str.rsplit("\n", 1)[0]
    return json.loads(json_str)


if __name__ == "__main__":
    cli()

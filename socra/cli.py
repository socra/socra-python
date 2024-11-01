import click
from pydantic import ConfigDict

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
from socra.prompts import Prompt
import socra
from socra.utils.decorators import throttle
from socra.utils.spinner import Spinner
import json
import os


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
    )
    agent.add_child(
        Agent(
            key="await_user_input",
            name="Await User Input",
            description="Await user input from the console before continuing. Useful when you need to ask a question or gather more information from the user.",
            runs=await_user_input,
        )
    )

    agent.add_child(
        Agent(
            key="file_system",
            name="interact with file system",
            description="Create, update, and manipulate files on the local file system. Call to perform any actions on files.",
            children=[
                Agent(
                    key="update_file",
                    name="Update File",
                    description="Update the contents of a file.",
                    runs=update_file,
                ),
                Agent(
                    key="create_file",
                    name="Create File",
                    description="Create a new file.",
                    runs=create_file,
                ),
                # Agent(
                #     key = "read_file",
                #     name = "Read File",
                #     description = "Read the contents of a file.",
                # ),
            ],
        )
    )
    agent.add_child(
        Agent(
            key="do_nothing",
            name="Do Nothing",
            description="Do nothing. Should be called when no further action is needed.",
            runs=do_nothing,
        )
    )

    agent.add_child(
        Agent(
            key="respond",
            name="Respond",
            description="Respond to the user with a message. Useful for providing a resolution or an update.",
            runs=respond,
        )
    )

    ctx = Context()
    if prompt:
        ctx.add_message(Message(role=Message.Role.HUMAN, content=prompt))

    idx = 0
    while idx < 5:
        idx += 1
        agent.run(ctx)

        # if last invocation was do_nothing, break
        if ctx.history[-1] == "do_nothing":
            print("No further actions needed.")
            break

    print("Cost")
    print("Num completions:", len(ctx.completions))
    print(ctx.token_cost)


import typing


class Context(Schema):

    messages: typing.List[Message] = []

    # history of action invocations
    history: typing.List[str] = []

    token_cost: TokenCost = TokenCost(
        input=0,
        output=0,
        total=0,
    )

    completions: typing.List[socra.Completion] = []

    # allow arbitrary types
    model_config: ConfigDict = {
        "arbitrary_types_allowed": True,
    }

    def track_completion(self, completion: socra.Completion):
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
        prompt = as_decision_prompt.format(
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
        prompt = socra.Prompt(
            messages=[
                *context.messages,
                socra.Message(
                    role=socra.Message.Role.HUMAN,
                    content=decision_prompt.format(children=children_str),
                ),
            ]
        )
        model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
        spinner = Spinner(message=f"Making decision for {self.name}")

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


def await_user_input(context: Context):
    res = input("What do you need?: ")
    context.add_message(Message(role=Message.Role.HUMAN, content=res))


def do_nothing(context: Context):
    context.add_message(
        Message(role=Message.Role.ASSISTANT, content="Decided to do nothing.")
    )


def update_file(context: Context):

    # first, we need to get the file path from the context
    file_path = get_file_path(context)

    # next, make sure file path exists
    if not os.path.exists(file_path):
        return f"File path '{file_path}' does not exist"

    # determine if the file should be updated.
    should_update = should_update_file_content(context, file_path)

    # now, we'll perform an action to modify the file.
    if should_update:
        modify_file_content(context, file_path)


def create_file(context: Context):
    """
    Create a new file
    """
    file_path = get_file_path(context)

    # next, make sure file path does not exist
    if os.path.exists(file_path):
        return f"File path '{file_path}' already exists"

    # next, create the file with blank content
    write_file(file_path, "")
    spinner = Spinner(message="Creating a new file")
    spinner.message = f"Creating a new file at {file_path}"
    spinner.finish()
    context.add_thought(f"Created a new file at {file_path}")

    # finally, we'll modify the file content
    modify_file_content(context, file_path)

    # prompt = socra.Prompt(
    #     messages=[
    #         *context.messages,
    #         socra.Message(
    #             role=socra.Message.Role.HUMAN,
    #             content=create_file_prompt,
    #         ),
    #     ]
    # )
    # model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
    # spinner = Spinner(message="Creating a new file")

    # @throttle(0.1)
    # def on_chunk(chunk):
    #     spinner.spin()

    # cr = socra.Completion(
    #     model,
    #     prompt,
    #     # mock_response=inputs.mock_response,
    #     on_chunk=on_chunk,
    # )
    # resp = cr.process()
    # context.track_completion(cr)

    # content = resp.content
    # dct = parse_json(content)
    # if "file_path" not in dct:
    #     raise ValueError("Missing 'file_path' in response")
    # if "content" not in dct:
    #     raise ValueError("Missing 'content' in response")

    # file_path = dct["file_path"]
    # content = dct["content"]

    # thought = f"Created a new file at {file_path}"
    # spinner.message = thought
    # spinner.finish()
    # context.add_thought(thought)
    # write_file(file_path, content)


# create_file_prompt = """Based on the context above, create a new file.

# Your response must be in JSON format, and should include the following keys:
# - file_path: The path of the new file. Include the file name and extension.
# - content: The content of the new file

# Example:
# {{
#     "file_path": "...",
#     "content": "..."
# }}

# Respond only in JSON format.
# """


def get_file_path(context: Context) -> str:

    prompt = socra.Prompt(
        messages=[
            *context.messages,
            socra.Message(
                role=socra.Message.Role.HUMAN,
                content=get_file_path_prompt,
            ),
        ]
    )
    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
    spinner = Spinner(message=f"Getting file path")

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
    if "path" not in dct:
        raise ValueError("Missing 'path' in response")

    path = dct["path"]
    thought = f"Extracted file path: {path}"
    spinner.message = thought
    spinner.finish()

    return path


get_file_path_prompt = """Based on the context above, extract the file path from the context.

Your response must be in JSON format, and should include the following keys:
- path: The path of the file

Example:
{{
    "path": "...",
}}

Respond only in JSON format.
"""


def should_update_file_content(context: Context, file_path: str) -> bool:
    """
    Decide if file path should be update.
    """

    file_content = read_file(file_path)

    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)

    prompt = socra.Prompt(
        messages=[
            *context.messages,
            socra.Message(
                role=socra.Message.Role.HUMAN,
                content=should_update_file_content_prompt.format(content=file_content),
            ),
        ]
    )

    spinner = Spinner(message=f"Deciding whether to update {file_path}")

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

    # parse JSON response
    dct = parse_json(content)

    if "should_update" not in dct:
        raise ValueError("Missing 'should_update' in response")
    if "reason" not in dct:
        raise ValueError("Missing 'reason' in response")

    should_update = dct["should_update"]

    if should_update:
        message = f"Decided to update {file_path} because {dct['reason'].lower()}"
    else:
        message = f"Decided not to update {file_path} because {dct['reason'].lower()}"

    spinner.message = message
    spinner.finish()
    context.add_thought(message)
    return should_update


should_update_file_content_prompt = """Base on the context above and the content below, decide whether or not the file should be updated.


File content:
<content>
{content}
</content>

Your response must be in JSON format, and should include the following keys:
- should_update: Boolean value indicating whether the file should be updated
- reason: Extremely brief thought on why the file should be updated or not

Example if the file should be updated:
{{
    "should_update": true,
    "reason": "the file..."
}}

Example if the file should not be updated:
{{
    "should_update": false,
    "reason": "the file..."
}}

Respond only in JSON format.
"""


def modify_file_content(context: Context, file_path: str):
    file_content = read_file(file_path)

    prompt = socra.Prompt(
        messages=[
            *context.messages,
            socra.Message(
                role=socra.Message.Role.HUMAN,
                content=modify_file_content_prompt.format(content=file_content),
            ),
        ]
    )
    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
    spinner = Spinner(message="Modifying the file content")

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
    if "content" not in dct:
        raise ValueError("Missing 'content' in response")
    if "reasoning" not in dct:
        raise ValueError("Missing 'reasoning' in response")

    content = dct["content"]
    reasoning = dct["reasoning"]

    thought = f"Modified the file content: {reasoning}"
    spinner.message = thought
    spinner.finish()
    context.add_thought(thought)
    write_file(file_path, content)


modify_file_content_prompt = """Based on the context above, modify the below file content.

File content:
<content>
{content}
</content>

Your response must be in JSON format, and should include the following keys:
- content: The new content of the file
- reasoning: Extremely brief thought on what was updated and why

Example:
{{
    "content": "...",
    "reasoning": "the content..."
}}

Respond only in JSON format.
"""


as_decision_prompt = """
- key: {key}
  name: {name}
  description: {description}
"""


decision_prompt = """Based on the context above, which action should be taken?

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

import click

from socra.commands.describe import Describe

from dotenv import load_dotenv
from socra.nodes import Node
from socra.nodes.actions.add_child import NodeAddChild
from socra.nodes.actions.content_update import NodeContentUpdate
from socra.nodes.actions.root import ActionKey, NodeRootAction


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
    print("adding improve")

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


# @click.group()
# @click.version_option()
# @click.pass_context
# def cli(ctx):
#     pass


if __name__ == "__main__":
    cli()

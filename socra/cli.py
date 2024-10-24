import click

from socra.commands.describe import Describe

from dotenv import load_dotenv
from socra.actions.files.modify_file import ActionImproveFile
from socra.files import File


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

    f = File(target)

    r = f.should_update(prompt)
    if r.should_update:
        f.update(prompt)


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

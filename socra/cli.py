import click

from socra.commands.describe import Describe
from socra.commands.improve import Improve

from dotenv import load_dotenv


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

    command = Improve(config=Improve.Config(target=target, prompt=prompt))
    command.execute()


@cli.command()
@click.argument("target", type=click.Path(exists=True))
@click.argument("prompt", type=click.STRING, required=False)
def describe(target: str, prompt: str):
    """Describe the specified file or directory."""

    command = Describe(config=Describe.Config(target=target, prompt=prompt))
    command.execute()


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    pass


if __name__ == "__main__":
    cli()

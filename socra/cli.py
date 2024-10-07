import click

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
@click.option(
    "--level",
    type=click.Choice(["low", "medium", "high"], case_sensitive=False),
    default="medium",
    help="Improvement level.",
)
def improve(target: str, level, prompt: str):
    """Improve the specified file or directory."""
    print(f"Improving '{target}' with prompt '{prompt}'.")
    print("target", type(target))
    print("prompt", type(prompt), prompt)

    command = Improve(config=Improve.Config(target=target, prompt=prompt))
    command.execute()


@cli.command()
@click.argument("target", type=click.Path(exists=True))
@click.option(
    "--format",
    type=click.Choice(["json", "yaml", "xml"], case_sensitive=False),
    default="json",
    help="Output format for the description.",
)
def describe(target, format):
    """Describe the specified file or directory."""
    print(f"Describing '{target}' in '{format}' format.")


if __name__ == "__main__":
    cli()

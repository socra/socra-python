import os

from socra.commands.command import Command
from socra.schemas.schema import Schema


class ImproveConfig(Schema):
    target: str
    prompt: str = None


class Improve(Command):

    Config = ImproveConfig

    def __init__(self, config: ImproveConfig):

        self.config = config

    def execute(self):

        # first, let's make sure target exists
        if not os.path.exists(self.config.target):
            raise FileNotFoundError(f"Target '{self.config.target}' not found.")

        # make sure target is a file (for now)
        if not os.path.isfile(self.config.target):
            raise ValueError(f"Target '{self.config.target}' must be a file.")

        # get file contents
        with open(self.config.target, "r") as file:
            contents = file.read()

        # next, let's execute a prompt to improve the contents

        print("executing improve command with config", self.config)

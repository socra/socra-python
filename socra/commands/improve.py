import os
import typing

from socra.commands.command import Command
from socra.schemas.base import Schema
from socra.io.files import read_file, write_file
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.messages.ai import AIMessageChunk
import logging

from socra.utils.decorators import throttle
from socra.utils.spinner import Spinner


def log(message: str):
    logging.info(message)


class ImproveConfig(Schema):
    target: str
    prompt: str = None


class ChunkPayload(Schema):
    chunk: str
    aggregate: str


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
        file_contents = read_file(self.config.target)

        # next, let's execute a prompt to improve the contents
        # TODO: instantiate llm elsewhere and make it super configurable
        llm = ChatOpenAI(model="gpt-4o-mini")
        messages: typing.List[BaseMessage] = [
            SystemMessage(content=system_prompt.format(prompt=self.config.prompt)),
            HumanMessage(content=file_contents),
        ]

        spinner = Spinner(message=f"Improving {self.config.target}")

        @throttle(0.1)
        def on_chunk(stream_chunk: ChunkPayload):
            spinner.spin()

        aggregate: AIMessageChunk = None
        for chunk in llm.stream(messages):
            aggregate: AIMessageChunk = (
                chunk if aggregate is None else aggregate + chunk
            )
            stream_chunk = ChunkPayload(
                chunk=chunk.content,
                aggregate=aggregate.content,
            )

            on_chunk(stream_chunk)

        spinner.finish()

        content = aggregate.content

        if content.startswith("```"):
            # remove first and last line
            content = "\n".join(content.split("\n")[1:-1])

        write_file(self.config.target, content)


system_prompt = """You are an expert code improver.
Given some code, you will improve it with the following prompt:
"{prompt}"

Return only the improved code and nothing else.
"""

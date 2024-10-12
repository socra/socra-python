import os
import typing
import sys

from socra.commands.command import Command
from socra.schemas.schema import Schema
from socra.io.files import read_file
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.messages.ai import AIMessageChunk

from socra.utils.decorators import throttle
from socra.utils.spinner import Spinner


class DescribeConfig(Schema):
    target: str
    prompt: str | None = None


class ChunkPayload(Schema):
    chunk: str
    aggregate: str


class Describe(Command):
    Config = DescribeConfig

    def __init__(self, config: DescribeConfig):
        self.config = config

    def execute(self):
        if not os.path.isfile(self.config.target):
            raise ValueError(f"Target '{self.config.target}' must be a file.")

        file_contents = read_file(self.config.target)

        # next, let's execute a prompt to improve the contents
        # TODO: instantiate llm elsewhere and make it super configurable
        llm = ChatOpenAI(model="gpt-4o-mini")

        messages: typing.List[BaseMessage] = [
            SystemMessage(
                content=system_prompt.format(
                    prompt=self.config.prompt if self.config.prompt else ""
                )
            ),
            HumanMessage(content=file_contents),
        ]

        spinner = Spinner(message=f"Describe {self.config.target}")

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

        # print content to stdout
        sys.stdout.write(content)


system_prompt = """You are an expert code describer.
Given some code, you will provide a concise description/summary of the code.
{prompt}

Return only your summary and nothing else.
"""

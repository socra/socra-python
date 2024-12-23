from socra.schemas import Schema
from socra.models import Model
from socra.prompts import Prompt
import typing

from langchain_openai import ChatOpenAI

from langchain_core.messages.ai import AIMessageChunk
from socra.completions.usage import TokenUsage, TokenCost


class MockResponse(Schema):
    content: str
    usage: TokenUsage
    enabled: bool = False


class CompletionResponseOutput(Schema):
    content: str
    usage: TokenUsage
    cost: TokenCost


class ChunkPayload(Schema):
    chunk: str
    aggregate: str


class Completion:
    def __init__(
        self,
        model: Model,
        prompt: Prompt,
        mock_response: MockResponse = None,
        on_chunk: typing.Optional[typing.Callable[[ChunkPayload], None]] = None,
    ):
        self.model = model
        self.prompt = prompt
        self._mock_response = mock_response
        self.on_chunk = on_chunk

        self.response: CompletionResponseOutput = None

    def process(self) -> CompletionResponseOutput:
        if self._mock_response and self._mock_response.enabled:
            content = self._mock_response.content
            token_usage = self._mock_response.usage
        else:
            llm = ChatOpenAI(model=self.model.key.value)
            prompt_messages = self.prompt.to_langchain()

            if self.on_chunk is not None:
                aggregate = None
                for chunk in llm.stream(prompt_messages, stream_usage=True):
                    aggregate: AIMessageChunk = (
                        chunk if aggregate is None else aggregate + chunk
                    )
                    stream_chunk = ChunkPayload(
                        chunk=chunk.content,
                        aggregate=aggregate.content,
                    )

                    self.on_chunk(stream_chunk)

                content = aggregate.content
                token_usage = TokenUsage(
                    input=aggregate.usage_metadata["input_tokens"],
                    output=aggregate.usage_metadata["output_tokens"],
                    total=aggregate.usage_metadata["total_tokens"],
                )
            else:
                response = llm.invoke(prompt_messages)
                content = response.content
                token_usage = TokenUsage(
                    input=response.response_metadata["token_usage"]["prompt_tokens"],
                    output=response.response_metadata["token_usage"][
                        "completion_tokens"
                    ],
                    total=response.response_metadata["token_usage"]["total_tokens"],
                )

        # next, format response
        token_cost = TokenCost.for_model(self.model, token_usage)

        self.response = CompletionResponseOutput(
            content=content,
            usage=token_usage,
            cost=token_cost,
        )

        return self.response

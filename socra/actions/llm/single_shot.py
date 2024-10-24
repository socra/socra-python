from socra.actions import Action, TInput, TOutput
from socra.schemas import Schema
from socra.prompts import Prompt
from socra.models import Model
import typing
from socra.completions.completion_response import (
    ChunkPayload,
    CompletionResponse,
    MockResponse,
    CompletionResponseOutput,
)


class LLMSingleShotInput(Schema):
    model: Model
    prompt: Prompt
    # callable
    on_chunk: typing.Callable[[ChunkPayload], None]
    mock_response: MockResponse = None


class LLMSingleShotAction(Action[LLMSingleShotInput, CompletionResponseOutput]):

    def run(self, params) -> TOutput:
        cr = CompletionResponse(
            params.model,
            params.prompt,
            mock_response=params.mock_response,
            on_chunk=params.on_chunk,
        )
        resp = cr.process()
        return resp

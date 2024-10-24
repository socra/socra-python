import typing
from socra.schemas import Schema
from socra.constants import Constants
from decimal import Decimal

import tiktoken


class ModelCost(Schema):
    input: Decimal
    output: Decimal


class Model(Schema):
    Key: typing.ClassVar = Constants.AI.Model.Key

    key: Constants.AI.Model.Key
    name: str

    cost: ModelCost
    """
    Cost per token or generation, where applicable.
    E.g.:
        $0.50 / 1M input tokens => 5.0e-7
        $1.00 / 1M output tokens => 1.0e-6

        cost = ModelCost(
            input=5.0e-7,
            output=1.0e-6,
        )
    """

    def get_encoding(self):
        return tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens for piece of text.
        Note that anthropic does not provide docs on this,
        so we're using gpt-4 as a reference.
        """
        encoding = self.get_encoding()
        return len(encoding.encode(text))

    @classmethod
    def for_key(cls, key: Constants.AI.Model.Key) -> "Model":
        return next(m for m in ALL_MODELS if m.key == key)


ALL_MODELS: typing.List[Model] = [
    Model(
        key=Model.Key.GPT_4O_MINI_2024_07_18,
        name="GPT4o Mini 2024-07-18",
        # context_window=16_384,
        context_window=128_000,
        is_latest=True,
        cost=ModelCost(
            input=Decimal("0.15") / Decimal(1_000_000),
            output=Decimal("0.60") / Decimal(1_000_000),
        ),
    ),
]

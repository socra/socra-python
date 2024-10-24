from socra.schemas import Schema
from socra.constants import Constants
from decimal import Decimal

import tiktoken


class ModelCost(Schema):
    input: Decimal
    output: Decimal


class Model(Schema):

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

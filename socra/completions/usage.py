from socra.schemas import Schema
from socra.models import Model


class TokenUsage(Schema):
    input: int
    output: int
    total: int

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            input=self.input + other.input,
            output=self.output + other.output,
            total=self.total + other.total,
        )


class TokenCost(Schema):
    input: float
    output: float
    total: float

    def __add__(self, other: "TokenCost") -> "TokenCost":
        return TokenCost(
            input=self.input + other.input,
            output=self.output + other.output,
            total=self.total + other.total,
        )

    @classmethod
    def for_model(
        cls,
        model: Model,
        token_usage: TokenUsage,
    ):
        cost_input = model.cost.input * token_usage.input
        cost_output = model.cost.output * token_usage.output
        cost_total = cost_input + cost_output
        return cls(
            input=cost_input,
            output=cost_output,
            total=cost_total,
        )

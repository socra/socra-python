import socra

from socra.completions.base import MockResponse
from socra.completions.usage import TokenUsage


def test_decision():
    """
    Basic test to make sure a decision can be made between two options given some context.
    """

    decision = socra.Decision.make(
        context=socra.Context(
            messages=[
                socra.Message(
                    role=socra.Message.Role.HUMAN, content="I want to create a file"
                )
            ]
        ),
        options=[
            socra.Option(
                key="create_file", name="Create a file", description="Create a file."
            ),
            socra.Option(
                key="create_folder",
                name="Create a folder",
                description="Create a folder.",
            ),
        ],
        config=socra.DecisionConfig(
            mock_response=MockResponse(
                content=r'{"key": "create_file", "reasoning": "I want to create a file"}',
                usage=TokenUsage(input=10, output=10, total=20),
                enabled=True,
            )
        ),
    )
    assert decision.option.key == "create_file"
    assert decision.reasoning == "I want to create a file"

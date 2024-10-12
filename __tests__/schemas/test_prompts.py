from socra.core.prompt import Prompt


class TestPrompts:

    def test_instantiation(self):
        """
        - can instantiate a blank prompt
        - can add messages to a prompt
        - can instantiate a prompt with messages
        """

        prompt = Prompt()
        assert len(prompt.messages) == 0

        prompt.add_message(
            Prompt.Message(role=Prompt.Message.Role.SYSTEM, content="hello world")
        )
        assert len(prompt.messages) == 1

        prompt = Prompt(
            messages=[
                Prompt.Message(role=Prompt.Message.Role.SYSTEM, content="hello world")
            ]
        )
        assert len(prompt.messages) == 1

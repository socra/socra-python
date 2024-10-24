import socra


class TestPrompts:
    def test_instantiation(self):
        """
        - can instantiate a blank prompt
        - can add messages to a prompt
        - can instantiate a prompt with messages
        """

        prompt = socra.Prompt()
        assert len(prompt.messages) == 0

        prompt.add_message(
            socra.Message(role=socra.Message.Role.SYSTEM, content="hello world")
        )
        assert len(prompt.messages) == 1

        prompt = socra.Prompt(
            messages=[
                socra.Message(role=socra.Message.Role.SYSTEM, content="hello world")
            ]
        )
        assert len(prompt.messages) == 1

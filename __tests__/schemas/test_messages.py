import socra


class TestMessages:
    def test_instantiation(self):
        """
        - can instantiate a message
        - can instantiate a message with multiple parts
        - can instantiate a message with a name
        - can instantiate message with different roles
        """

        # can instantiate a message
        message = socra.Message(role=socra.Message.Role.SYSTEM, content="hello world")
        assert message.role == socra.Message.Role.SYSTEM
        assert len(message.content) == 1
        assert message.content[0].text == "hello world"

        # can instantiate a message with multiple parts
        message = socra.Message(
            role=socra.Message.Role.SYSTEM,
            content=[socra.Message.Part(text="Hello world")],
        )

        assert message.role == socra.Message.Role.SYSTEM
        assert len(message.content) == 1
        assert message.content[0].text == "Hello world"

        # can instantiate a message with a name
        message = socra.Message(
            role=socra.Message.Role.SYSTEM,
            content=[socra.Message.Part(text="Hello world")],
            name="name",
        )
        assert message.name == "name"

        # can instantiate message with different roles
        message = socra.Message(role=socra.Message.Role.HUMAN, content="hello world")
        assert message.role == socra.Message.Role.HUMAN
        message = socra.Message(
            role=socra.Message.Role.ASSISTANT, content="hello world"
        )
        assert message.role == socra.Message.Role.ASSISTANT

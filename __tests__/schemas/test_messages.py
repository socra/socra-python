from socra.core.messages import Message


class TestMessages:
    def test_instantiation(self):
        """
        - can instantiate a message
        - can instantiate a message with multiple parts
        - can instantiate a message with a name
        - can instantiate message with different roles
        """

        # can instantiate a message
        message = Message(role=Message.Role.SYSTEM, content="hello world")
        assert message.role == Message.Role.SYSTEM
        assert len(message.content) == 1
        assert message.content[0].text == "hello world"

        # can instantiate a message with multiple parts
        message = Message(
            role=Message.Role.SYSTEM, content=[Message.Part(text="Hello world")]
        )

        assert message.role == Message.Role.SYSTEM
        assert len(message.content) == 1
        assert message.content[0].text == "Hello world"

        # can instantiate a message with a name
        message = Message(
            role=Message.Role.SYSTEM,
            content=[Message.Part(text="Hello world")],
            name="name",
        )
        assert message.name == "name"

        # can instantiate message with different roles
        message = Message(role=Message.Role.HUMAN, content="hello world")
        assert message.role == Message.Role.HUMAN
        message = Message(role=Message.Role.ASSISTANT, content="hello world")
        assert message.role == Message.Role.ASSISTANT

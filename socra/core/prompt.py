import typing


from socra.schemas.schema import Schema

from socra.core.messages import Message


class Prompt(Schema):
    Message: typing.ClassVar = Message

    messages: typing.List[Message] = []

    def add_message(self, message: "Message"):
        self.messages.append(message)
        return self

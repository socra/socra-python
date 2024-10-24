import typing


from socra.schemas import Schema

from socra.core.messages import Message


class Prompt(Schema):

    messages: typing.List[Message] = []

    def add_message(self, message: Message):
        self.messages.append(message)
        return self

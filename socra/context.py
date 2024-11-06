from socra.schemas import Schema
from socra.messages import Message
import typing


class Context(Schema):
    """
    Core context object. Functions similar to an HTTP Request object,
    where context can be passed around. Context contains messages,
    and agents use context to make decisions.
    """

    messages: typing.List[Message] = []

    def add_message(self, message: Message, inplace: bool = False) -> "Context":
        """
        Add a message to the context.
        If inplace is True, the message will be added to the context in place.
        Use inplace = False when you don't want to modify the original context.
        """

        if inplace:
            self.messages.append(message)
            return self
        else:
            return Context(messages=self.messages + [message])

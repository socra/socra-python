import typing

from pydantic import ValidationError, model_validator
from langchain.schema import (
    AIMessage as LCAIMessage,
    HumanMessage as LCHumanMessage,
    SystemMessage as LCSystemMessage,
)

from socra.schemas import Schema
from socra.messages import Message
from socra.models import Model


class Prompt(Schema):
    messages: typing.List[Message] = []

    def to_json(self):
        return {
            "messages": [m.to_json() for m in self.messages],
        }

    @classmethod
    def from_json(cls, dct: dict):
        return cls(
            messages=[Message.from_json(m) for m in dct["messages"]],
        )

    def to_langchain(
        self,
    ) -> typing.List[LCAIMessage | LCHumanMessage | LCSystemMessage]:
        """Convert a prompt to a langchain prompt"""
        return [m.to_langchain() for m in self.messages]

    @model_validator(mode="before")
    @classmethod
    def validate_messages(cls, data: typing.Any) -> dict:
        return_data = {}

        if not isinstance(data, dict):
            raise ValidationError("data should be a dict")

        messages = data.get("messages")
        # if messages is None:
        #     raise ValidationError("messages should be included")

        # convert string to list of messages

        if isinstance(messages, str):
            messages = [Message(role=Message.Role.HUMAN, content=messages)]

        if messages is not None and not isinstance(messages, list):
            raise ValidationError("messages should be a list")

        # validate system message
        # should be max of 1 system message,
        # and if present should be first
        system_message_count = 0
        if messages is not None:
            for i, message in enumerate(messages):
                if not isinstance(message, Message):
                    raise ValidationError(
                        f"message at index {i} should be an instance of Message"
                    )
                if message.role == Message.Role.SYSTEM:
                    system_message_count += 1
                    if i != 0:
                        raise ValidationError("system message should be first message")

            if system_message_count > 1:
                raise ValidationError("only one system message is allowed")

            return_data["messages"] = messages

        return return_data

    def add_message(self, message: Message):
        if not isinstance(message, Message):
            raise ValueError("message should be an instance of Message")
        self.messages.append(message)
        return self

    def limit_context_window(
        self, model: Model, buffer_tokens: int = None, max_tokens: int = None
    ):
        """Limit the context wndow to a certain number of tokens.
        Returns a new prompt with the context window limited.

        buffer_tokens: number of tokens to leave as buffer
        max_tokens: maximum number of tokens to include in the context window
            - used IFF provided and < model context window

        Strategy:
        - include system message
        - traverse other messages, starting from the end
        - include messages until we're at the limit
        """

        system_messages = [m for m in self.messages if m.role == Message.Role.SYSTEM]
        other_messages = [m for m in self.messages if m.role != Message.Role.SYSTEM]

        system_message_token_count = sum(
            [m.count_tokens(model) for m in system_messages]
        )

        model_limit = model.context_window
        if max_tokens is not None and max_tokens < model_limit:
            model_limit = max_tokens

        buffer_tokens = buffer_tokens if buffer_tokens is not None else 0

        # max number of tokens other_messages can occupy
        calculated_max_tokens = model_limit - system_message_token_count - buffer_tokens

        # iterate through messages, starting from the end
        limited_messages: typing.List[Message] = []
        num_tokens = 0
        for message in reversed(other_messages):
            message_tokens = message.count_tokens(model)
            if num_tokens + message_tokens > calculated_max_tokens:
                break

            limited_messages.append(message)
            num_tokens += message_tokens

        limited_messages.reverse()

        # return a new prompt with the limited messages
        return Prompt(messages=system_messages + limited_messages)

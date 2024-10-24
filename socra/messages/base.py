import typing

from enum import Enum
from socra.schemas.base import Schema
from pydantic import model_validator
from langchain.schema import (
    AIMessage as LCAIMessage,
    HumanMessage as LCHumanMessage,
    SystemMessage as LCSystemMessage,
)


if typing.TYPE_CHECKING:
    from socra.models import Model


class MessageRole(Enum):
    SYSTEM = "system"
    HUMAN = "human"
    ASSISTANT = "assistant"


class ContentPartType(Enum):
    TEXT = "text"
    """
    Text content.
    """

    # TODO: file, other message types


class ContentPart(Schema):
    """
    Individual part of a message.
    """

    Type: typing.ClassVar = ContentPartType

    type: ContentPartType = ContentPartType.TEXT
    text: str

    def to_json(self):
        return {
            "type": self.type.value,
            "text": self.text,
        }

    def count_tokens(self, model: "Model") -> int:
        """Count total tokens for content part"""
        if self.type == ContentPart.Type.TEXT:
            return model.count_tokens(self.text)
        raise ValueError(f"Invalid type {self.type} for ContentPart.")

    @classmethod
    def from_json(cls, dct: dict):
        """Deserialize from JSON"""

        type_str = dct.get("type")
        type = cls.Type(type_str)
        if type == cls.Type.TEXT:
            return cls(type=type, text=dct.get("text"))

        raise ValueError(f"Invalid type {type} for ContentPart.")


class Message(Schema):
    """
    Generic messag object, comprised of:
    - role: MessageRole
    - parts: List[ContentPart]
    - name: str
    """

    Part: typing.ClassVar = ContentPart
    Role: typing.ClassVar = MessageRole

    role: MessageRole
    content: typing.List[ContentPart] = []
    name: str = None

    # field validator for content
    @model_validator(mode="before")
    @classmethod
    def validate_message(cls, data: typing.Any) -> dict:
        content = data.get("content")
        if isinstance(content, str):
            content = [ContentPart(type=ContentPart.Type.TEXT, text=content)]
            data["content"] = content

        return data

    def to_json(self):
        dct = {
            "role": self.role.value,
        }
        if self.name:
            dct["name"] = self.name

        if len(self.content) == 1:
            dct["content"] = self.content[0].text
        else:
            dct["content"] = [part.to_json() for part in self.content]

    def to_langchain(self) -> LCAIMessage | LCHumanMessage | LCSystemMessage:
        dct = self.to_json()

        if self.role == Message.Role.HUMAN:
            return LCHumanMessage(content=dct["content"])
        elif self.role == Message.Role.SYSTEM:
            return LCSystemMessage(content=dct["content"])
        elif self.role == Message.Role.ASSISTANT:
            return LCAIMessage(content=dct["content"])

        raise ValueError(f"Invalid role {self.role} for Message.")

    def count_tokens(self, model: Model) -> int:
        """Count total tokens for message, taking into account
        that the message might be content of parts
        """

        if self.content:
            return model.count_tokens(self.content)

        total_tokens = 0
        for part in self.content:
            total_tokens += part.count_tokens(model)

        return total_tokens

    @classmethod
    def from_json(cls, dct: dict):
        """Deserialize from JSON"""

        role_str = dct.get("role")
        role = Message.Role(role_str)
        content = dct.get("content")
        parts = dct.get("parts")
        name = dct.get("name")

        kw = {
            "role": role,
        }

        if content:
            kw["content"] = content

        if parts:
            kw["parts"] = [ContentPart.from_json(p) for p in parts]

        if name:
            kw["name"] = name

        return cls(**kw)

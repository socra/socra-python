import typing

from enum import Enum
from socra.schemas.schema import Schema
from pydantic import model_validator


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

    # @model_validator(mode="before")
    # @classmethod
    # def validate_content_part(cls, data: typing.Any) -> dict:
    #     return_data = {}

    #     if not isinstance(data, dict):
    #         raise ValidationError("data should be a dict")

    #     type_str = data.get("type")
    #     if type is None:
    #         raise ValidationError("type should be included")

    #     try:
    #          = ContentPart.Type(type)
    #     except ValueError as e:
    #         raise ValidationError(e) from e

    #     return_data["type"] = type

    #     if type == ContentPart.Type.TEXT:
    #         text = data.get("text")
    #         if text is None:
    #             raise ValidationError(f"text should be included for type {type}")

    #         return_data["text"] = text
    #     else:
    #         raise NotImplementedError(f"Type {type} not implemented")

    #     return return_data


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

    # def to_json(self):
    #     dct = {
    #         "role": self.role.value,
    #     }
    #     if self.name:
    #         dct["name"] = self.name

    #     if len(self.content) == 1:
    #         dct["content"] = self.content[0].to_json()["text"]
    #     else:
    #         dct["content"] = [p.to_json() for p in self.content]

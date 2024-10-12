import typing


from socra.schemas.schema import Schema

from socra.core.messages import Message


class Prompt(Schema):
    system: typing.Optional[Message] = None
    messages: typing.List[Message] = []

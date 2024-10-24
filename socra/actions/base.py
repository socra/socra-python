from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Any
from typing_extensions import get_args
import inspect

from pydantic import BaseModel, create_model


TInput = TypeVar("TInput", contravariant=True)
TOutput = TypeVar("TOutput", covariant=True)


class Action(Generic[TInput, TOutput], ABC):
    """
    Parent Action class, from which all other class-based actions inherit.

    Key pieces of functionality:
    - On instantiation, actions have access to the context of the run.
    - Actions must implement a run method, which is called when the action
        is executed.
    - run() is called with explicit inputs for the action.
    """

    @abstractmethod
    def run(self, params: TInput) -> TOutput:
        pass

    @property
    def InputType(self) -> Type[TInput]:
        """
        The input type for this Action. Inferred from the Generic input type.
        Can be overriden explicitly in subclasses (but you probably shouldn't).
        """
        return self.__class__.__annotations__.get("params", Any)

    @property
    def OutputType(self) -> Type[TOutput]:
        """
        The output type for this Action. Inferred from the Generic output type.
        Can be overriden explicitly in subclasses (but you probably shouldn't).
        """
        return self.__class__.__annotations__.get("return", Any)

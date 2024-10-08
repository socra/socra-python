from abc import ABC, abstractmethod


class Command(ABC):
    """
    The Command interface declares a method for executing a command.

    Implement an `execute` method that encapsulates the code of a specific
    operation.

    """

    @abstractmethod
    def execute(self) -> None:
        pass

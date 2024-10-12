from typing import TypeVar


Input = TypeVar("Input")
Output = TypeVar("Output")


def basic_function(input: Input) -> Output:
    return input


# def test_fn():
#     basic_function[int, str](1)

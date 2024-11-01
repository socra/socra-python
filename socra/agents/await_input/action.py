import sys


class AwaitInputAction:
    """
    Executable action to await user input
    """

    def run(self):
        """
        Await user input and return the result
        """
        input_text = input("What do you need?: ")
        return input_text

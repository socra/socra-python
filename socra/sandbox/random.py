class Calculator:
    """A simple calculator class to perform basic arithmetic operations."""

    @staticmethod
    def here_is_a_func():
        """Returns the sum of 1 and 1.

        Returns:
            int: The result of 1 + 1, which is 2.
        """
        return 1 + 1

    @staticmethod
    def multiply(a, b):
        """Returns the product of two numbers.

        Args:
            a (int or float): The first number to multiply.
            b (int or float): The second number to multiply.

        Returns:
            int or float: The product of a and b.
        """
        return a * b

    @staticmethod
    def add(a, b):
        """Returns the sum of two numbers.

        Args:
            a (int or float): The first number to add.
            b (int or float): The second number to add.

        Returns:
            int or float: The sum of a and b.
        """
        return a + b

    @staticmethod
    def subtract(a, b):
        """Returns the difference of two numbers.

        Args:
            a (int or float): The number from which to subtract.
            b (int or float): The number to subtract.

        Returns:
            int or float: The difference of a and b.
        """
        return a - b

    @staticmethod
    def divide(a, b):
        """Returns the quotient of two numbers.

        Args:
            a (int or float): The numerator.
            b (int or float): The denominator.

        Returns:
            float: The quotient of a and b.

        Raises:
            ValueError: If b is zero.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    @staticmethod
    def power(base, exponent):
        """Returns the result of raising a base to an exponent.

        Args:
            base (int or float): The base number.
            exponent (int or float): The exponent to raise the base to.

        Returns:
            int or float: The result of base raised to exponent.
        """
        return base**exponent

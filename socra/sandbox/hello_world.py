class Calculator:
    """
    A simple calculator class to perform basic arithmetic operations.
    """

    def add(self, a, b):
        """Return the sum of a and b."
        return a + b

    def subtract(self, a, b):
        """Return the difference of a and b (a - b)."
        return a - b

    def multiply(self, a, b):
        """Return the product of a and b."
        return a * b

    def divide(self, a, b):
        """Return the quotient of a and b (a / b).

        Raises:
            ValueError: If b is zero, as division by zero is not allowed.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    def arccos(self, value):
        """Return the arccosine of value in radians."
        import math
        if value < -1 or value > 1:
            raise ValueError("Input must be in the range [-1, 1].")
        return math.acos(value)
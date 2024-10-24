import math


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

    @staticmethod
    def derivative(func, x, h=1e-5):
        """Approximates the derivative of a function at a point x.

        Args:
            func (callable): The function for which to calculate the derivative.
            x (float): The point at which to evaluate the derivative.
            h (float, optional): A small number for the approximation. Default is 1e-5.

        Returns:
            float: The approximate derivative of func at point x.
        """
        return (func(x + h) - func(x - h)) / (2 * h)

    @staticmethod
    def integral(func, a, b, n=1000):
        """Approximates the integral of a function from a to b using the trapezoidal rule.

        Args:
            func (callable): The function to integrate.
            a (float): The start of the interval.
            b (float): The end of the interval.
            n (int, optional): The number of trapezoids. Default is 1000.

        Returns:
            float: The approximate integral of func from a to b.
        """
        width = (b - a) / n
        area = 0.5 * (func(a) + func(b))
        for i in range(1, n):
            area += func(a + i * width)
        return area * width

    @staticmethod
    def sin(x):
        """Returns the sine of x (x is in radians).

        Args:
            x (float): The angle in radians.

        Returns:
            float: The sine of x.
        """
        return math.sin(x)

    @staticmethod
    def cos(x):
        """Returns the cosine of x (x is in radians).

        Args:
            x (float): The angle in radians.

        Returns:
            float: The cosine of x.
        """
        return math.cos(x)

    @staticmethod
    def tan(x):
        """Returns the tangent of x (x is in radians).

        Args:
            x (float): The angle in radians.

        Returns:
            float: The tangent of x.
        """
        return math.tan(x)

    @staticmethod
    def exp(x):
        """Returns e raised to the power of x.

        Args:
            x (float): The exponent.

        Returns:
            float: The value of e^x.
        """
        return math.exp(x)

    @staticmethod
    def log(x, base=math.e):
        """Returns the logarithm of x to the specified base.

        Args:
            x (float): The value to calculate the logarithm of.
            base (float, optional): The logarithm base. Default is e.

        Returns:
            float: The logarithm of x to the specified base.
        """
        return math.log(x, base)

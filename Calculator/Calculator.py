from Addition.Addition import *
from Subtraction.Subtraction import *
from Multiplication.Multiplication import *
from Division.Division import *
from Clear.Clear import *

class NumberAdder:
    """A simple class to add two numbers."""

    def add(self, num1, num2):
        """
        Adds two numbers and returns the result.

        Parameters:
            num1 (int/float): The first number.
            num2 (int/float): The second number.

        Returns:
            int/float: The sum of num1 and num2.
        """
        return num1 + num2

class NumberSubtractor:
    """A class to perform subtraction of two numbers."""

    def subtract(self, num1, num2):
        """
        Subtract num2 from num1 and return the result.

        Parameters:
            num1 (int/float): The first number.
            num2 (int/float): The second number to be subtracted from the first number.

        Returns:
            int/float: The result of the subtraction.
        """
        return num1 - num2

class Multiplier:
    """A simple class to perform multiplication of two numbers."""

    def multiply(self, a, b):
        """
        Multiplies two numbers and returns the result.

        Parameters:
            a (int/float): The first number.
            b (int/float): The second number.

        Returns:
            int/float: The product of the two numbers.
        """
        return a * b

class Divider:
    """A class to perform division of two numbers."""

    def divide(self, num1, num2):
        """
        Divides num1 by num2 and returns the result.

        Parameters:
            num1 (float or int): The numerator.
            num2 (float or int): The denominator.

        Returns:
            float: The result of the division.

        Raises:
            ValueError: If num2 is zero, as division by zero is not allowed.
        """
        if num2 == 0:
            raise ValueError("Cannot divide by zero.")
        return num1 / num2

class Calculator:
    def __init__(self):
        # Initialize the calculation result
        self.result = 0

    def add(self, value):
        """Add a value to the current result."""
        self.result += value

    def subtract(self, value):
        """Subtract a value from the current result."""
        self.result -= value

    def multiply(self, value):
        """Multiply the current result by a value."""
        self.result *= value

    def divide(self, value):
        """Divide the current result by a value. Handle division by zero."""
        if value == 0:
            raise ValueError("Cannot divide by zero.")
        self.result /= value

    def clear_result(self):
        """Clear the current calculation result."""
        # Set the result to zero
        self.result = 0
        print("Result cleared.")

# Example usage:
calc = Calculator()
calc.add(10)
calc.subtract(5)
print(f"Current Result: {calc.result}")  # Output: Current Result: 5

calc.clear_result()
print(f"Current Result after clearing: {calc.result}")  # Output: Current Result after clearing: 0
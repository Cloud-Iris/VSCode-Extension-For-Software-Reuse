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
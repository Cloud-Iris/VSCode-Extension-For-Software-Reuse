class NumberSubtractor:
    """
    A class to perform subtraction of two numbers.
    
    Methods:
        subtract(num1, num2): Subtracts num2 from num1 and returns the result.
    """

    def subtract(self, num1, num2):
        """
        Subtract num2 from num1 and return the result.

        Parameters:
            num1 (int/float): The first number.
            num2 (int/float): The second number to be subtracted from the first number.

        Returns:
            int/float: The result of the subtraction.
        """
        # Perform the subtraction
        result = num1 - num2
        
        # Return the result
        return result

# Example usage:
if __name__ == "__main__":
    subtractor = NumberSubtractor()
    result = subtractor.subtract(10, 5)
    print("The result of subtraction is:", result)
class Divider:
    """
    A class to perform division of two numbers.
    
    Methods:
        divide(num1, num2): Divides num1 by num2 and returns the result.
    """

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

# Example usage:
if __name__ == "__main__":
    divider = Divider()
    
    try:
        result = divider.divide(10, 2)
        print(f"Result: {result}")
        
        # This will raise an exception
        result = divider.divide(5, 0)
        print(f"Result: {result}")
    except ValueError as e:
        print(e)
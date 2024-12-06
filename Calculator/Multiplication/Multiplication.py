class Multiplier:
    """
    A simple class to perform multiplication of two numbers.
    
    Methods:
        multiply(a, b): Multiplies two numbers and returns the result.
    """

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

# Example usage:
if __name__ == "__main__":
    multiplier = Multiplier()
    result = multiplier.multiply(3, 4)
    print(f"The product of 3 and 4 is {result}")
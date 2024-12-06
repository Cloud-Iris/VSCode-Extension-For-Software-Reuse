class NumberAdder:
    """
    A simple class to add two numbers.
    
    Methods:
        add(num1, num2): Adds two numbers and returns the result.
    """

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

# Example usage:
if __name__ == "__main__":
    adder = NumberAdder()
    result = adder.add(5, 3)
    print(f"The sum is: {result}")
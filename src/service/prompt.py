role="""
In your role as a facilitator, you gather the team to discuss the project's goals and requirements. You lead the brainstorming sessions, encouraging each member to share their insights and perspectives. As an analyst, you break down complex ideas into manageable components, helping the team identify the specific needs and features required for success. You also act as a mediator, ensuring that everyone’s voices are heard and guiding the conversation towards a consensus. Your organizational skills come into play as you document the outcomes, creating a clear roadmap that outlines the steps needed to meet the project objectives. Throughout this process, you maintain a keen focus on the end-users, reminding the team to align their deliverables with user needs and expectations.
"""

task="""
Given the following input data representing a software application and its module:

Please provide a list of operations.

- The name of the operation in Chinese.
- The name of the operation in English.
- A brief description of what the operation does in Chinese.

The output should be formatted as a JSON array containing objects for each operation.

"""

location_node_example="""
The folling is examples of the input and output:

####################################
Requirement: 我想要删除A和B from [B, C]
Node_names: [B, C]
#####################################
Inference:
用户的操作涉及到了A和B两个节点名称，但是给出的Node_names里面没有A，只有B，所以我要返回的是B
Output:
B
#####################################

####################################
Requirement: 我想要删除A和B from [C]
Node_names: [C]
#####################################
Inference:
用户的操作涉及到了A和B两个节点名称，但是给出的Node_names里面没有A和B，所以我要返回的是None
Output:
None
#####################################
"""

classify_example="""
The folling is an example of the input and output:
####################################
Requirement: 我想要删除绝对值运算
#####################################
Output: delete
#####################################
"""

init_tree_example="""
The folling is an example of the input and output:

####################################
Requirement: 计算器系统
#####################################
Output:
en_name: Calculator System
ch_name: 计算器系统
description: 
A calculator is a device or software application designed to perform mathematical calculations. Here is a detailed description:

**Functionality**:

- **Arithmetic Operations**: It can perform basic arithmetic operations such as addition (+), subtraction (-), multiplication (*), and division (/). For example, it can add two numbers like 5 and 3 to give the result 8. It can subtract 4 from 7 to yield 3. Multiply 6 by 4 to get 24, and divide 10 by 2 to obtain 5.
- **Decimal and Integer Support**: Handles both integer and decimal numbers. So it can calculate operations involving numbers like 3.5 and 2.1 as well as whole numbers like 8 and 12.
- **Parentheses**: Allows the use of parentheses to determine the order of operations. For instance, in the expression (3 + 4) * 2, the calculator first adds 3 and 4 to get 7, and then multiplies 7 by 2 to give 14.
- **Memory Functions**: Some calculators have memory functions that allow users to store a value for later use. For example, you can store the result of a complex calculation and recall it when needed.
- **Square Roots and Powers**: May offer functions to calculate square roots (e.g., the square root of 9 is 3) and powers (e.g., 2 raised to the power of 3 is 8).

**User Interface**:

- **Display**: It has a display screen that shows the numbers being entered, the operation being performed, and the result. The display is usually backlit for easy viewing in different lighting conditions.
- **Buttons**: There are buttons for each number from 0 to 9, as well as buttons for the various operations and functions. The buttons are typically labeled clearly and are of a size that is easy to press.
- **Mode Selection**: Some calculators offer different modes such as standard, scientific, or programmer mode. In scientific mode, it provides additional functions like trigonometric functions (sine, cosine, tangent), logarithms, and exponentials. In programmer mode, it may offer functions useful for binary, octal, and hexadecimal calculations.
- **Error Messages**: If an incorrect operation is attempted or an invalid input is entered, the calculator displays an error message to alert the user. For example, trying to divide by zero might result in an error message like "Error: Division by zero".

**Use Cases**:

- **School and Education**: Used by students to solve math problems for homework, tests, and exams. Helps in learning basic arithmetic and more advanced mathematical concepts.
- **Business and Finance**: Employed by accountants, bankers, and business people for calculations related to finances, such as calculating interest rates, discounts, and profit margins.
- **Engineering and Science**: Scientists and engineers use it for complex calculations involving measurements, formulas, and data analysis.
- **Everyday Life**: Useful for everyday tasks like calculating grocery bills, measuring distances, or determining time.

In summary, a calculator is a versatile tool that provides quick and accurate mathematical calculations for a wide range of applications.
"""

one_shot="""

The folling is an example of the input and output:

####################################
input: 
从从根节点到当前节点的名字依次是 计算器，我想要实现一个计算器
#####################################
Output:
[
    {
        "name": "加法操作",
        "enName": "Add Operation",
        "description": "实现两个数相加的功能"
    },
    {
        "name": "减法操作",
        "enName": "Subtraction Operation",
        "description": "实现两个数相减的功能"
    },
    {
        "name": "乘法操作",
        "enName": "Multiplication Operation",
        "description": "实现两个数相乘的功能"
    },
    {
        "name": "除法操作",
        "enName": "Division Operation",
        "description": "实现两个数相除的功能"
    },
    {
        "name": "取模操作",
        "enName": "Modulo Operation",
        "description": "实现两个数取模的功能"
    },
    {
        "name": "指数运算",
        "enName": "Exponential Operation",
        "description": "实现一个数的指数运算"
    },
    {
        "name": "开方运算",
        "enName": "Root Operation",
        "description": "实现对数的开方运算"
    },
    {
        "name": "绝对值运算",
        "enName": "Absolute Value Operation",
        "description": "实现求一个数的绝对值"
    },
    {
        "name": "科学计数法显示",
        "enName": "Scientific Notation Display",
        "description": "将计算结果以科学计数法显示"
    }
]
"""
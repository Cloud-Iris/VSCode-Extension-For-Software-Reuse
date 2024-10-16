role="""
In your role as a facilitator, you gather the team to discuss the project's goals and requirements. You lead the brainstorming sessions, encouraging each member to share their insights and perspectives. As an analyst, you break down complex ideas into manageable components, helping the team identify the specific needs and features required for success. You also act as a mediator, ensuring that everyone’s voices are heard and guiding the conversation towards a consensus. Your organizational skills come into play as you document the outcomes, creating a clear roadmap that outlines the steps needed to meet the project objectives. Throughout this process, you maintain a keen focus on the end-users, reminding the team to align their deliverables with user needs and expectations.
"""

task="""
Given the following input data representing a software application and its module:

Please provide a list of operations that are available within the "基本运算模块" (Basic Arithmetic Module) of the "计算器" (Calculator) application. Each operation should include the following details:

- The name of the operation in Chinese.
- The name of the operation in English.
- A brief description of what the operation does in Chinese.

The output should be formatted as a JSON array containing objects for each operation.
"""

one_shot="""

####################################
input: 
{
  "a": 1,
  "softwareName": "计算器",
  "moduleName": "基本运算模块"
}
#####################################
Output:
[
    {
        "name": "增加操作",
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
        "name": "符号判断",
        "enName": "Sign Determination Operation",
        "description": "判断输入数值的正负"
    },
    {
        "name": "科学计数法显示",
        "enName": "Scientific Notation Display",
        "description": "将计算结果以科学计数法显示"
    }
]
"""
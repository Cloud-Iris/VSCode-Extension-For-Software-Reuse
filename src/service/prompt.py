role="""
As an analyst, you break down complex ideas into manageable components.

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

case1:
####################################
Requirement: 我想要删除A和B from [B, C]
Node_names: [B, C]
#####################################
Inference:
用户的操作涉及到了A和B两个节点名称，但是给出的Node_names里面没有A，只有B，所以我要返回的是B
#####################################
Output:
B
#####################################

case2:
####################################
Requirement: 我想要删除A和B from [C]
Node_names: [C]
#####################################
Inference:
用户的操作涉及到了A和B两个节点名称，但是给出的Node_names里面没有A和B，所以我要返回的是None
#####################################
Output:
None
#####################################
"""

classify_example="""
The folling is an example of the input and output:
####################################
Requirement: 我想要A操作
#####################################
Output: A
#####################################
"""

init_tree_example="""
The folling is an example of the input and output:

####################################
Requirement: A系统
#####################################
Output:
en_name: A System
ch_name: A系统
description: 
A system is a device or software application designed to perform various operations. Here is a detailed description:xxx

"""

one_shot="""

The folling is an example of the input and output:

####################################
Inference:
用户想要对 A 进行功能拆解, 我认为 A 需要具有 B, C, D, E 等功能，所以返回B, C, D, E
####################################
Output:
[
    {
        "chName": "中文名",
        "enName": "B Operation",
        "description": "实现xxx功能"
    },
    {
        "chName": "中文名",
        "enName": "C Operation",
        "description": "实现xxx功能"
    },
    {
        "chName": "中文名",
        "enName": "D Operation",
        "description": "实现xxx功能"
    },
    {
        "chName": "中文名",
        "enName": "E Operation",
        "description": "实现xxx功能"
    }
]
"""

one_shot2="""

The following is an example of the input and output:

####################################
input: 
从根节点到当前节点的名字依次是 Z->计算器，请对 计算器 进行功能拆解
#####################################
Inference:
用户想要对 计算器 进行功能拆解, 我认为 计算器 需要具有 加法, 减法, 乘法, 除法 等功能，所以返回 加法, 减法, 乘法, 除法
####################################
Output:
[
    {
        "name": "加法",
        "enName": "Add Operation",
        "description": "实现两个数相加的功能"
    },
    {
        "name": "减法",
        "enName": "Subtraction Operation",
        "description": "实现两个数相减的功能"
    },
    {
        "name": "乘法",
        "enName": "Multiplication Operation",
        "description": "实现两个数相乘的功能"
    },
    {
        "name": "除法",
        "enName": "Division Operation",
        "description": "实现两个数相除的功能"
    }
]
"""
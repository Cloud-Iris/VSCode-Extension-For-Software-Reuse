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
用户想要对 A 进行功能拆解, 我认为 A 需要具有 B, C功能，所以返回B, C
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
    }
]
"""

process_json_example="""
####################################
Input:
我想要把B移动到C下面
{
  "ch_name": "A",
  "children": [
    {
      "ch_name": "B",
      "children": []
    },
    {
      "ch_name": "C",
      "children": []
    }
  ]
}
####################################
Inference:
因为并没有涉及A这个节点，所以我需要将A原封不动地返回，因为要将C移动到B下面，所以C要被放在B的children里面，所以我要返回的是
####################################
Output:
```json
{
  "ch_name": "A",
  "children": [
    {
      "ch_name": "C",
      "children": [
        {
          "ch_name": "B",
          "children": []
        }
      ]
    }
  ]
}
```
####################################
"""

import json
import ollama
import re
from prompt import role, task, one_shot
from requirement_tree.requirement_tree_node import RequirementTreeNode, RequirementInternalNode, RequirementLeafNode

# 将用户输入的需求分类为create, modify, add, delete
def requirements_classification(s:str) -> str:
    # create, modify, add, delete
    prompt = f"Classify the following requirement into one of the categories: modify, add, delete. Only one word is returned. \nRequirement: {s}"
    res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
    classification = res['message']['content'].lower()
    print(classification)
    if "modify" in classification:
        return "modify"
    elif "add" in classification:
        return "add"
    elif "delete" in classification:
        return "delete"
    else:
        raise ValueError("Unable to classify the requirement.")

def decompose_requirements(input):
    """
    Decompose the requirements into a list of requirements.
    """

    # input = """
    # {
    # "a": 1,
    # "softwareName": "计算器",
    # "moduleName": "基本运算模块"
    # }
    # """
    res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": role + task + input + one_shot}], options={"temperature": 0})

    # 提取 message 的 content
    content = res['message']['content']
    pattern = r'\[([^\]]*)\]'

    matches = re.findall(pattern, content)
    
    s="["
    # 打印匹配结果
    for match in matches:
        s+=match
    s+="]"
    return s

def user_confirm():
    """
    Confirm the requirements.
    """
    response = input("你确认执行吗[y]/n: ").strip().lower()
    return response == 'y' or response == ''

# 将叶子结点转换为内部结点
def convert_leaf_to_internal(leaf_node):
    new_internal_node = RequirementInternalNode(leaf_node.en_name, leaf_node.ch_name, "新的描述（反映中间节点功能）", leaf_node.file_path, [])
    if leaf_node.parent:
        parent_node = leaf_node.parent
        parent_node.replace_child(leaf_node, new_internal_node)
    return new_internal_node


def user_interaction():
    # 初始化根节点
    root = RequirementLeafNode('root', '根节点', '根节点的描述', '文件路径')
    location = root
    print("你好，请问有什么我可以帮忙的吗：")
    s = input()
    while s.lower() not in ["no", "q", "quit", "exit"]:
        classify = requirements_classification(s)
        # e.g. 我想要创建一个计算器
        # e.g. 我想要添加所有的计算功能
        # e.g. 我想要在加法里面添加二进制加法功能
        if classify.startswith("add"):
            convert_leaf_to_internal(location, RequirementLeafNode('leaf', 'leaf', 'leaf', 'leaf'))
            children = decompose_requirements(s)
            children = json.loads(children)
            # To Do: location节点更新，添加子节点，树状结构输出所有节点
            print(children)

        # e.g. 我想要删除加法功能
        if classify.startswith("delete"):
            # To Do: location节点删除，树状结构输出所有节点
            pass
        # e.g. 我想要把加法功能修改成减法功能
        if classify.startswith("modify"):
            # To Do: location节点修改，树状结构输出所有节点
            pass
        print("你好，请问接下来要对哪个节点操作？")
        # To Do: location节点更新
        
        print("你好，请问有什么我可以帮忙的吗：")
        s = input()

user_interaction()
import json
import ollama
import re
from prompt import role, task, one_shot
from requirement_tree.requirement_tree import RequirementTree

# 将用户输入的需求分类为create, modify, add, delete
def requirements_classification(s:str) -> str:
    # create, modify, add, delete
    prompt = f"Classify the following requirement into one of the categories: modify, add, delete. Only one word is returned. \nRequirement: {s}"
    res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
    classification = res['message']['content'].lower()
    # print(classification)
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

    input = "The input that you should process is:\n"+input.strip()

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

def get_path_to_current_node(tree):
    """
    获取从根节点到当前节点的所有ch_name
    @param tree: 需求树对象
    @return: 从根节点到当前节点的所有ch_name组成的列表
    """
    path = []
    node = tree.current_node
    while node is not None:
        path.append(node.ch_name)
        node = node.parent
    path.reverse()  # 从根节点到当前节点
    return path

def dfs_search(node, ch_name):
    """
    深度优先搜索树中的节点
    @param node: 当前节点
    @param ch_name: 要搜索的节点的中文名称
    @return: 匹配的节点，如果未找到则返回None
    """
    if node.ch_name == ch_name:
        return node
    if hasattr(node, 'children') and node.children:
        for child in node.children:
            result = dfs_search(child, ch_name)
            if result:
                return result
    return None

def display_tree(node, depth=0):
    """
    按照节点的深度输出树状结构
    @param node: 当前节点
    @param depth: 当前节点的深度
    """
    print("\t" * depth + node.ch_name)
    if hasattr(node, 'children') and node.children:
        for child in node.children:
            display_tree(child, depth + 1)

def init_tree(s):
    """
    初始化一个RequirementTree
    @param s: 用户输入的需求描述
    @return: 初始化后的RequirementTree
    """

    prompt = """
    You are a top-notch description expert. 
    For the following requirement: {requirement}. 
    Write a detailed description to satisfy the requirement.
    Incorporate best practices and add comments where necessary. 
    """.format(requirement=s)
    
    # 调用ollama.chat API获取描述
    res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
    description = res['message']['content']
    
    # 初始化RequirementTree
    tree = RequirementTree('Calculator', "计算器", description, '')
    return tree

def display_node(node):
    print(f"=====================\n当前节点的信息如下所示：\n=====================\nen_name: {node.en_name}\nch_name: {node.ch_name}\ndescription: {node.description}\ncode: {node.code}\nfile_path: {node.file_path}\n=====================")

def user_interaction():
    # 初始化根节点
    print("你好，请问您需要实现什么系统：")
    s = input()
    tree = init_tree(s)
    while s.lower() not in ["no", "q", "quit", "exit"]:
        classify = requirements_classification(s)
        # e.g. 我想要创建一个计算器
        # e.g. 我想要添加所有的计算功能
        # e.g. 我想要在加法里面添加二进制加法功能
        if classify.startswith("add"):
            # 获取从根节点到当前节点的所有ch_name
            path = get_path_to_current_node(tree)
            # 将路径信息添加到s中
            s = "从根节点到当前节点的名字依次是 " + " -> ".join(path) + " 在当前节点我想要实现： " +s
            
            # 按照谢老师的意思，需要把从根节点到当前节点的所有信息传递过去
            tree.convert_leaf_to_internal(tree.current_node)
            children = decompose_requirements(s)
            children = json.loads(children)
            for child in children:
                tree.add_child(child['enName'], child['name'], child['description'], '')
            print("=====================\n当前树结构如下：\n=====================")
            display_tree(tree.root)
            print("=====================")

        # e.g. 我想要删除加法功能
        elif classify.startswith("delete"):
            display_node(tree.current_node)
            response = input("你确认删除当前节点吗[y]/n: ").strip().lower()
            if response == 'y' or response == '':
                name = tree.current_node.ch_name
                tree.current_node = tree.current_node.parent
                tree.remove_child(name)
            print("=====================\n当前树结构如下：\n=====================")
            display_tree(tree.root)
            print("=====================")

        # e.g. 我想要把加法功能修改成减法功能
        elif classify.startswith("modify"):
            display_node(tree.current_node)
            # 询问用户需要修改成什么
            new_en_name = input(f"请输入新的英文名称，或者回车跳过，当前数据是: {tree.current_node.en_name} ").strip() or tree.current_node.en_name
            new_ch_name = input(f"请输入新的中文名称，或者回车跳过，当前数据是: {tree.current_node.ch_name} ").strip() or tree.current_node.ch_name
            new_description = input(f"请输入新的描述，或者回车跳过，当前数据是: {tree.current_node.description} ").strip() or tree.current_node.description
            new_code = input(f"请输入新的代码，或者回车跳过，当前数据是: {tree.current_node.code}) ").strip() or tree.current_node.code
            new_file_path = input(f"请输入新的文件路径，或者回车跳过，当前数据是: {tree.current_node.file_path} ").strip() or tree.current_node.file_path

            print(new_ch_name)
            print(tree.current_node.ch_name)
            tree.modify_current_node(new_en_name, new_ch_name, new_description, new_code, new_file_path)

            print(tree.current_node.ch_name)
            print("=====================\n当前树结构如下：\n=====================")
            display_tree(tree.root)
            print("=====================")
        else:
            print("对不起，我无法理解您的需求，请详细描述您的增删改需求。")
        
        print("你好，请问接下来要对哪个名字的节点操作？输入q/quit/exit/no退出系统。")
        child_name = input().strip()
        while(1):
            if child_name.lower() in ["no", "q", "quit", "exit"]:
                return
            # 使用DFS搜索节点
            target_node = dfs_search(tree.root, child_name)
            if target_node:
                tree.current_node = target_node
                break
            else:
                print(f"未找到名为 {child_name} 的节点，请重新输入，或者输入q/quit/exit/no退出系统。")
                child_name = input().strip()

        print("你好，请问你要对这个节点进行什么操作？输入q/quit/exit/no退出系统。")
        s = input()

user_interaction()
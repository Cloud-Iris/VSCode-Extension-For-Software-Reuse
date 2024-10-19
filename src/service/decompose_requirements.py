import json
import ollama
import re
from prompt import role, task, one_shot
from requirement_tree.requirement_tree import RequirementTree

class RequirementManager:
    def __init__(self):
        self.tree = None
        self.node_names = None

    def requirements_classification(self, s: str) -> str:
        """
        将用户输入的需求分类为create, modify, add, delete, code
        """
        prompt = f"Classify the following requirement into one of the categories: modify, add, delete, code. Only one word is returned. \nRequirement: {s}"
        res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        classification = res['message']['content'].lower()
        if "modify" in classification:
            return "modify"
        elif "add" in classification:
            return "add"
        elif "delete" in classification:
            return "delete"
        elif "code" in classification:
            return "code"
        else:
            raise ValueError("Unable to classify the requirement.")

    def decompose_requirements(self, input):
        """
        Decompose the requirements into a list of requirements.
        """
        input = "The input that you should process is:\n" + input.strip()
        res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": role + task + input + one_shot}], options={"temperature": 0})
        content = res['message']['content']
        pattern = r'\[([^\]]*)\]'
        matches = re.findall(pattern, content)
        s = "["
        for match in matches:
            s += match
        s += "]"
        return s

    def user_confirm(self):
        """
        Confirm the requirements.
        """
        response = input("你确认执行吗[y]/n: ").strip().lower()
        return response == 'y' or response == ''

    def get_path_to_current_node(self):
        """
        获取从根节点到当前节点的所有ch_name
        @return: 从根节点到当前节点的所有ch_name组成的列表
        """
        path = []
        node = self.tree.current_node
        while node is not None:
            path.append(node.ch_name)
            node = node.parent
        path.reverse()  # 从根节点到当前节点
        return path

    def dfs_search(self, node, ch_name):
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
                result = self.dfs_search(child, ch_name)
                if result:
                    return result
        return None

    def display_tree(self, node, depth=0, display=True):
        """
        按照节点的深度输出树状结构
        @param node: 当前节点
        @param depth: 当前节点的深度
        """
        s= node.ch_name+", "
        if display:
            print("\t" * depth + node.ch_name)
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                s+=(self.display_tree(child, depth + 1, display))
        return s

    def init_tree(self, s):
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
        res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        description = res['message']['content']
        self.tree = RequirementTree('Calculator', "计算器", description, '')
        self.node_names = self.display_tree(self.tree.root, 0, False)

    def display_node(self, s, node):
        """
        显示节点的信息
        @param s: 显示的标题信息
        @param node: 要显示的节点
        """
        print("=====================\n{}\n=====================\nen_name: {}\nch_name: {}\ndescription: {}\ncode: {}\nfile_path: {}\n=====================".format(
            s, node.en_name, node.ch_name, node.description, node.code, node.file_path))

    def dfs_search_node_name(self, node, selected_node_name):
        """
        深度优先搜索树中的节点
        @param node: 当前节点
        @param selected_node_name: 要搜索的节点的中文名称
        @return: 匹配的节点，如果未找到则返回None
        """
        if node.ch_name in selected_node_name or selected_node_name in node.ch_name:
            return node
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                result = self.dfs_search_node_name(child, selected_node_name)
                if result:
                    return result
        return None

    def location_node(self, s):
        """
        根据用户输入的需求描述，定位到树中的一个节点
        """

        prompt = """
        You are a top-notch selection expert. 
        For the following requirement: {requirement}. 
        From the following list of node names, select the one that best matches the requirement. If not found, please return None.:
        {node_names}

        Only return the full name of the selected node.
        """.format(requirement=s, node_names="\n".join(self.node_names))
        
        res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        selected_node_name = res['message']['content'].strip().replace(" ", "")

        # print(f"=====================\n您选择的节点是：{selected_node_name}\n=====================")

        # 先看当前节点是不是
        if self.tree.current_node.ch_name in selected_node_name or selected_node_name in self.tree.current_node.ch_name:
            return self.tree.current_node
        # 再看当前节点的父节点是不是
        if self.tree.current_node.parent and (self.tree.current_node.parent.ch_name in selected_node_name or selected_node_name in self.tree.current_node.parent.ch_name) :
            return self.tree.current_node.parent
        # 再看当前节点的子节点是不是
        for child in self.tree.current_node.children:
            if child.ch_name in selected_node_name or selected_node_name in child.ch_name:
                return child
        # 最后dfs搜索整个树
        return self.dfs_search_node_name(self.tree.root, selected_node_name)        

    def user_interaction(self):
        # 初始化根节点
        print("请问您需要实现什么系统：")
        s = input()
        self.init_tree(s)
        while s.lower() not in ["no", "q", "quit", "exit"]:
            classify = self.requirements_classification(s)
            if classify.startswith("add"):
                path = self.get_path_to_current_node()
                s = "从根节点到当前节点的名字依次是 " + " -> ".join(path) + " 在当前节点我想要实现： " + s
                self.tree.convert_leaf_to_internal(self.tree.current_node)
                children = self.decompose_requirements(s)
                children = json.loads(children)
                for child in children:
                    self.tree.add_child(child['enName'], child['name'], child['description'], '')
                print("=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")
            elif classify.startswith("delete"):
                while self.tree.current_node != None:
                    not_delete=[]
                    self.display_node("您想要删除的节点信息如下所示", self.tree.current_node)
                    response = input("你确认删除{}吗[y]/n: ".format(self.tree.current_node.ch_name)).strip().lower()
                    if response == 'y' or response == '':
                        name = self.tree.current_node.ch_name
                        self.tree.current_node = self.tree.current_node.parent
                        self.tree.remove_child(name)
                    else:
                        not_delete.append(self.tree.current_node)
                    self.node_names = self.display_tree(self.tree.root, 0, False)
                    # 从self.node_names中删除not_delete
                    for node in not_delete:
                        self.node_names = self.node_names.replace(node.ch_name+", ", "")
                    self.tree.current_node = self.location_node(s)
                print("=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")
                self.tree.current_node = self.tree.root
            elif classify.startswith("modify"):
                self.display_node("您想要修改的节点信息如下所示", self.tree.current_node)
                new_en_name = input(f"请输入新的英文名称，或者回车跳过，当前是: {self.tree.current_node.en_name} ").strip() or self.tree.current_node.en_name
                new_ch_name = input(f"请输入新的中文名称，或者回车跳过，当前是: {self.tree.current_node.ch_name} ").strip() or self.tree.current_node.ch_name
                new_description = input(f"请输入新的描述，或者回车跳过，当前是: {self.tree.current_node.description} ").strip() or self.tree.current_node.description
                new_code = input(f"请输入新的代码，或者回车跳过，当前是: {self.tree.current_node.code}) ").strip() or self.tree.current_node.code
                new_file_path = input(f"请输入新的文件路径，或者回车跳过，当前是: {self.tree.current_node.file_path} ").strip() or self.tree.current_node.file_path
                self.tree.modify_current_node(new_en_name, new_ch_name, new_description, new_code, new_file_path)
                print("=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")
            elif classify.startswith("code"):
                self.tree.current_node = self.tree.root
                code = self.tree.construct_current_code()
                print(f"=====================\n所有代码生成完毕，根节点的代码如下所示：\n=====================\n{code}\n=====================")
            else:
                print("对不起，我无法理解您的需求，请详细描述您的需求。")
            print("\n请问您有什么进一步的需求？输入q/quit/exit/no退出系统。")
            s = input().strip()
            while True:
                if s.lower() in ["no", "q", "quit", "exit"]:
                    return
                self.tree.current_node = self.location_node(s)
                if self.tree.current_node is None:
                    print("\n对不起，我无法理解您的需求，请详细描述您的需求，或者输入q/quit/exit/no退出系统。")
                    s = input().strip()
                else:
                    break
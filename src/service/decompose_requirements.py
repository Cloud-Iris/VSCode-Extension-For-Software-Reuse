import json
import ollama
import re
from prompt import role, task, one_shot, location_node_example, init_tree_example, classify_example
from requirement_tree.requirement_tree import RequirementTree
from file_system.fileChange import *
from watchdog.observers import Observer
import threading
import time

class RequirementManager:
    def __init__(self, filepath):
        self.tree = None
        self.node_names = ""
        self.filepath = filepath

    def requirements_classification(self, s: str) -> str:
        """
        将用户输入的需求分类为create, modify, add, delete, code, show
        """

        prompt = """Classify the following requirement into one of the categories: modify, add, delete, code, show_information. Only one word is returned.
        Requirement: {requirement}
        {classify_example}
        """.format(requirement=s, classify_example=classify_example)
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
        elif "show_information" in classification:
            return "show"
        else:
            return None

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

        # 如果根目录有restore.json文件，加载树结构
        # if os.path.exists(self.filepath+"/restore.json"):
        #     self.flag=False
        #     self.tree = load_tree_from_json(self.filepath+"/restore.json")
        #     print("\n根目录系统加载完毕！")
        #     self.node_names = self.display_tree(self.tree.root)
        # else:
        print("\n目前根目录没有系统，请问您需要实现什么系统：")
        s = input()

        prompt = """
        You are a top-notch description expert. 
        Requirement: {requirement}. 

        Return the following information:
        First line: The English name of the requirement.
        Second line: The Chinese name of the requirement.
        Other lines: A detailed description to satisfy the requirement.

        {init_tree_example}
        """.format(requirement=s, init_tree_example=init_tree_example)
        res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        description = res['message']['content'].strip()
        lines = description.split('\n')

        for i in range(len(lines)):
            if "en_name" in lines[i]:
                en_name = re.sub(r'[^a-zA-Z]', '', lines[i].split(":")[1].strip().replace(" ",""))
            elif "ch_name" in lines[i]:
                ch_name = lines[i].split(":")[1].strip()
            elif "description" in lines[i]:
                detailed_description = "\n".join(lines[i+1:]).strip()
                break

        # print("en_name: {}\nch_name: {}\ndetailed_description: {}\ndescription: {}".format(en_name, ch_name, detailed_description, description))

        # 初始化 RequirementTree
        self.tree = RequirementTree(en_name, ch_name, detailed_description, '')
        self.node_names = self.display_tree(self.tree.root, 0, False)

    def display_node(self, s, node):
        """
        显示节点的信息
        @param s: 显示的标题信息
        @param node: 要显示的节点
        """
        print("=====================\n{}\n=====================\nen_name: {}\nch_name: {}\ndescription: {}\nfile_path: {}\ncode: {}\n=====================".format(
            s, node.en_name, node.ch_name, node.description, node.file_path, node.code))

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

    def start_watching(self):
        """
        启动文件监听器，监听指定目录中的文件修改事件。
        @param directory: 要监听的目录
        @param node_map: 文件名到节点的映射
        """
        event_handler = FileChangeHandler(self.tree.file_node_map, self.tree)
        observer = Observer()
        print("file_path: ", self.filepath)
        observer.schedule(event_handler, self.filepath, recursive=True)
        observer.start()

        def run_observer():
            """
            运行文件监听器的线程。
            """
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

        # 启动一个新的线程来运行文件监听器
        observer_thread = threading.Thread(target=run_observer)
        observer_thread.daemon = True
        observer_thread.start()

    def location_node(self, s):
        """
        根据用户输入的需求描述，定位到树中的一个节点
        """

        prompt = """
        Requirement: {requirement}.
        From the list of names below, choose the one that display in the requirement. 
        If none of the names display in the requirement, return None:
        Node_names: [{node_names}]
        Only return one word. 
        {location_node_example}
        """.format(requirement=s, node_names=self.node_names, location_node_example=location_node_example)

        res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        selected_node_name = res['message']['content'].strip()

        # 定位字符串中return的位置，只要return后面的内容
        if "return" in selected_node_name:
            selected_node_name = selected_node_name[selected_node_name.index("return")+6:].strip()
        elif "is:" in selected_node_name:
            selected_node_name = selected_node_name[selected_node_name.index("is:")+3:].strip()

        # print(f"=====================\n您选择的节点是：{selected_node_name}\n=====================")

        if self.tree.current_node==None:
            return self.dfs_search_node_name(self.tree.root, selected_node_name)
        # 先看当前节点是不是
        if self.tree.current_node.ch_name in selected_node_name or selected_node_name in self.tree.current_node.ch_name:
            if self.tree.current_node.ch_name not in self.node_names:
                return self.dfs_search_node_name(self.tree.root, selected_node_name)
            return self.tree.current_node
        # 再看当前节点的父节点是不是
        if self.tree.current_node.parent and (self.tree.current_node.parent.ch_name in selected_node_name or selected_node_name in self.tree.current_node.parent.ch_name) :
            if self.tree.current_node.ch_name not in self.node_names:
                return self.dfs_search_node_name(self.tree.root, selected_node_name)
            return self.tree.current_node.parent
        # 再看当前节点的子节点是不是
        for child in self.tree.current_node.children:
            if child.ch_name in selected_node_name or selected_node_name in child.ch_name:
                if self.tree.current_node.ch_name not in self.node_names:
                    return self.dfs_search_node_name(self.tree.root, selected_node_name)
                return child
        # 最后dfs搜索整个树
        return self.dfs_search_node_name(self.tree.root, selected_node_name)        

    def user_interaction(self):
        """
        用户交互函数，用于处理用户输入的需求并对需求树进行相应的操作。
        """
        # 初始化根节点
        s = ""
        classify = "add"
        self.init_tree(s)
        
        while s.lower() not in ["no", "q", "quit", "exit"]:
            
            if classify.startswith("add"):
                # 获取从根节点到当前节点的所有ch_name
                path = self.get_path_to_current_node()
                # 将路径信息添加到s中
                s = "从根节点到当前节点的名字依次是 " + " -> ".join(path) + " 在当前节点我想要实现： " + s
                
                # 将当前节点转换为内部节点
                self.tree.convert_leaf_to_internal(self.tree.current_node)
                # 分解需求
                children = self.decompose_requirements(s)
                children = json.loads(children)
                # 添加子节点
                for child in children:
                    self.tree.add_child(child['enName'].replace(" ",""), child['name'].replace("增加","").replace("添加",""), child['description'], '')
                
                # 显示当前树结构
                print("\n=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")
            
            elif classify.startswith("delete"):
                not_delete = [self.tree.root.ch_name]
                # 循环删除节点，直到用户确认删除
                while self.tree.current_node is not None:
                    self.display_node("您想要删除的节点信息如下所示", self.tree.current_node)
                    response = input("你确认永久删除{}吗[y]/n: ".format(self.tree.current_node.ch_name)).strip().lower()
                    if response == 'y' or response == '':
                        self.tree.current_node.remove_node()
                    else:
                        not_delete.append(self.tree.current_node.ch_name)
                    # print(not_delete)
                    # 更新树结构并显示
                    self.node_names = self.display_tree(self.tree.root, 0, False)
                    # 从self.node_names中删除not_delete
                    for node_name in not_delete:
                        if node_name+", " in self.node_names:
                            self.node_names = self.node_names.replace(node_name+", ", "")
                    # print(self.node_names)
                    self.tree.current_node = self.location_node(s)
                
                # 显示当前树结构
                print("\n=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")
                self.tree.current_node = self.tree.root
            
            elif classify.startswith("modify"):
                # 显示当前节点信息并询问用户需要修改成什么
                self.display_node("您想要修改的节点信息如下所示", self.tree.current_node)
                new_en_name = input(f"请输入新的英文名称，回车保留当前数据： {self.tree.current_node.en_name} ").strip() or self.tree.current_node.en_name
                new_ch_name = input(f"请输入新的中文名称，回车保留当前数据: {self.tree.current_node.ch_name} ").strip() or self.tree.current_node.ch_name
                new_description = input(f"请输入新的描述，回车保留当前数据: {self.tree.current_node.description} ").strip() or self.tree.current_node.description
                new_code = input(f"请输入新的代码，回车保留当前数据: {self.tree.current_node.code}) ").strip() or self.tree.current_node.code
                new_file_path = input(f"请输入新的文件路径，回车保留当前数据: {self.tree.current_node.file_path} ").strip() or self.tree.current_node.file_path
                self.tree.modify_current_node(new_en_name, new_ch_name, new_description, new_code, new_file_path)
                
                # 显示当前树结构
                print("\n=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")
            
            elif classify.startswith("code"):
                # 生成当前节点的代码
                self.tree.current_node = self.tree.root
                print("开始在目录{}生成代码...".format(self.filepath))
                self.tree.construct_current_code(self.filepath)
                # 创建文件夹和文件
                create_directory_and_files(self.tree.file_node_map,self.tree.current_node, self.filepath, [])
                save_tree_to_json(self.tree, self.filepath+"/restore.json")
                self.start_watching()
                print("=====================\n所有代码生成完毕！请在{}中查看\n=====================".format(self.filepath))
            
            elif classify.startswith("show"):
                self.display_node("您想要的节点信息如下所示", self.tree.current_node)

            else:
                # 显示当前树结构
                print("\n=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")
                print("对不起，我无法理解您的需求，请基于树结构详细描述您的需求。")
            
            # 询问用户是否有进一步的需求
            print("\n请问您有什么进一步的需求？输入q/quit/exit/no退出系统。")
            s = input().strip()
            while True:
                if s.lower() in ["no", "q", "quit", "exit"]:
                    return
                self.tree.current_node = self.location_node(s)
                if self.tree.current_node is None:
                    # 显示当前树结构
                    print("\n=====================\n当前树结构如下：\n=====================")
                    self.node_names = self.display_tree(self.tree.root)
                    print("=====================")
                    print("\n对不起，我无法理解您的需求，请详细描述您的需求，或者输入q/quit/exit/no退出系统。")
                    s = input().strip()
                else:
                    break
            # 分类用户输入的需求
            classify = self.requirements_classification(s)
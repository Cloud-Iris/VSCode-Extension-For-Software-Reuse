import json
import ollama
import re
from prompt import role, task, one_shot, location_node_example, init_tree_example, classify_example, one_shot2
from requirement_tree.requirement_tree import RequirementTree
from file_system.fileChange import *
from watchdog.observers import Observer
import threading
from difflib import SequenceMatcher
import time
import jieba.posseg as pseg

class RequirementManager:
    def __init__(self, filepath):
        self.tree = None
        self.node_names = []
        self.filepath = filepath

    def requirements_classification(self, s: str) -> str:
        """
        将用户输入的需求分类
        """

        str_node_names=",".join(self.node_names)

        res="n"
        classification=""

        while res not in ["y", ""]:
            prompt = """
            你是语言专家。
            将以下需求分类到以下类别之一：添加、删除、拆解、修改、生成代码、展示信息。仅返回一个词。
            需求：{requirement}
            分类的目的是判断用户想要对{node_names}中的某个节点进行何种操作
            """.format(requirement=s, node_names=str_node_names)
            res = ollama.chat(model="qwen2.5-coder:7b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
            classification = res['message']['content'].lower()
            print("请问你是想对{}进行{}操作吗 [y]/n".format(self.tree.current_node.ch_name, classification))
            res = input().strip().lower()
            if res == "n":
                print("请选择一种操作：添加、删除、拆解、修改、生成代码、展示信息。")
                s= input().strip().lower()

        if "修改" in classification:
            return "修改"
        elif "添加" in classification:
            return "添加"
        elif "删除" in classification:
            return "删除"
        elif "生成代码" in classification:
            return "生成代码"
        elif "展示信息" in classification:
            return "展示信息"
        elif "拆解" in classification:
            return "拆解"
        else:
            return ""

    def decompose_requirements(self, input):
        """
        Decompose the requirements into a list of requirements.
        """
        input = "The requirement that you should decompose is:\n" + input.strip()
        res = ollama.chat(
            model="qwen2.5-coder:7b", 
            stream=False, 
            messages=[{"role": "user", "content": role + input + one_shot}], 
            options={"temperature": 0},
        )
        content = res['message']['content']
        print("content: ", content)
        pattern = r'\[([^\]]*)\]'
        matches = re.findall(pattern, content)
        s = "["
        for match in matches:
            s += match
        s += "]"
        return s

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
        node_name = []
        node_name.append(node.ch_name)
        if display:
            print("\t" * depth + node.ch_name)
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                node_name.extend(self.display_tree(child, depth + 1, display))
        return node_name

    def init_tree(self) -> str:
        """
        初始化一个RequirementTree
        @param s: 用户输入的需求描述
        @return: 初始化后的RequirementTree
        """

        # 如果根目录的第一层文件夹中有restore.json文件，加载树结构
        try:
            root_dir = self.filepath
            for item in os.listdir(root_dir):
                item_path = os.path.join(root_dir, item)
                if os.path.isdir(item_path):
                    restore_path = os.path.join(item_path, "restore.json")
                    if os.path.exists(restore_path):
                        self.flag = False
                        self.tree = load_tree_from_json(restore_path)
                        print("\n根目录系统加载完毕！")
                        self.node_names = self.display_tree(self.tree.root)

                        # 询问用户是否有进一步的需求
                        print("\n请问您有什么进一步的需求？输入q/quit/exit/no退出系统。")
                        s = input().strip()
                        while True:
                            if s.lower() in ["no", "q", "quit", "exit"]:
                                os._exit(0)
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

                        return s, classify
        except Exception as e:
            # print(f"加载树结构时发生错误: {e}")
            pass

        # else:
        print("\n没有存档记录，请问您有什么新需求：")
        s = input()

        en_name, ch_name, detailed_description= self.generate_node(s)

        # print("en_name: {}\nch_name: {}\ndetailed_description: {}\ndescription: {}".format(en_name, ch_name, detailed_description, description))

        # 生成根节点
        self.tree = RequirementTree(en_name, ch_name, detailed_description, '')
        self.tree.current_node = self.tree.root
        self.node_names = self.display_tree(self.tree.root, 0, False)

        return s, "拆解"

    def generate_node(self, requirement):
        prompt = """
        You are a top-notch description expert. 
        Requirement: {requirement}. 

        Return the following information:
        First line: The English name of the requirement.
        Second line: The Chinese name of the requirement.
        Other lines: A detailed description to satisfy the requirement.

        {init_tree_example}
        """.format(requirement=requirement, init_tree_example=init_tree_example)
        res = ollama.chat(model="qwen2.5-coder:7b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        description = res['message']['content'].strip()
        lines = description.split('\n')

        for i in range(len(lines)):
            if "en_name" in lines[i]:
                en_name = re.sub(r'[^a-zA-Z]', '', lines[i].split(":")[1].strip().replace(" ","_"))
            elif "ch_name" in lines[i]:
                ch_name = lines[i].split(":")[1].strip()
            elif "description" in lines[i]:
                detailed_description = "\n".join(lines[i+1:]).strip()
                break
        return en_name, ch_name, detailed_description

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
        if node.ch_name in selected_node_name:
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
        observer.schedule(event_handler, self.tree.root.en_name, recursive=True)
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

    def location_node(self, s, type_name="other"):
        """
        根据用户输入的需求描述，定位到树中的一个节点
        """

        # prompt = """你是一个做选择题的专家。用户提出了这样的需求: {requirement} from [{node_names}]。请选择一个最符合用户需求的选项，如果没有符合的选项，请返回None:\
        # Return only the full name of the selected name without Spaces.\
        # {location_node_example}
        # """.format(requirement=s, node_names=", ".join(self.node_names), location_node_example=location_node_example)

        selected_node_name=""

        while selected_node_name not in self.node_names and selected_node_name != "None":
            if selected_node_name != "":
                selected_node_name = "你之前从列表中选择了"+selected_node_name+"，这个选择不在列表中，请从列表中选择一个。"
            if type_name == "other":
                prompt = """你是一个意图识别的专家。用户提出了这样的需求:{requirement}。\n\
请从列表[{node_names}]中识别支持用户执行该操作的最小单位。\n\
如果你觉得列表里面没有用户想要操作的节点，请返回第一个值。\n\
{selected_node_name}\n\
下面是一个输出示例：**一个词**""".format(
                    requirement=s, node_names=", ".join(self.node_names), selected_node_name=selected_node_name, location_node_example=location_node_example
                )
            elif type_name == "delete":
                prompt = """你是一个意图识别的专家。用户提出了这样的需求:{requirement}。\n\
请从列表[None, {node_names}]中识别支持用户执行该操作的最小单位。\n\
如果你觉得列表里面没有用户想要操作的节点，请返回None。\n\
{selected_node_name}\n\
下面是一个输出示例：**一个词**""".format(
                    requirement=s, node_names=", ".join(self.node_names), selected_node_name=selected_node_name, location_node_example=location_node_example
                )
            print("prompt: ", prompt)

            res = ollama.chat(model="qwen2.5-coder:7b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
            selected_node_name = res['message']['content'].strip()

            print(f"=====================\n筛选前：{selected_node_name}\n=====================")

            # 定位字符串中return的位置，只要return后面的内容
            if "return" in selected_node_name:
                selected_node_name = selected_node_name[selected_node_name.index("return")+6:].strip()
            if ":" in selected_node_name:
                selected_node_name = selected_node_name[selected_node_name.rindex(":")+1:].strip()
            if "output" in selected_node_name:
                selected_node_name = selected_node_name[selected_node_name.index("output")+6:].strip()
            if "Output" in selected_node_name:
                selected_node_name = selected_node_name[selected_node_name.index("Output")+6:].strip()
            if "```python" in selected_node_name:
                selected_node_name = selected_node_name[selected_node_name.index("```python")+8:selected_node_name.rindex("```")].strip()
                # selected_node_name只保留中文
                selected_node_name = "".join([word for word, flag in pseg.cut(selected_node_name) if flag == "x"])
            if "**" in selected_node_name:
                selected_node_name = selected_node_name[selected_node_name.index("**")+2:selected_node_name.rindex("**")].strip()
            
        # print("node_names: ", self.node_names)
        print(f"=====================\n大模型选择的节点是：{selected_node_name}\n=====================")

        if self.tree.current_node==None:
            return self.dfs_search_node_name(self.tree.root, selected_node_name)
        # 先看当前节点是不是
        if self.tree.current_node.ch_name == selected_node_name:
            if self.tree.current_node.ch_name not in self.node_names:
                return self.dfs_search_node_name(self.tree.root, selected_node_name)
            return self.tree.current_node
        # 再看当前节点的父节点是不是
        if self.tree.current_node.parent and self.tree.current_node.parent.ch_name == selected_node_name:
            if self.tree.current_node.ch_name not in self.node_names:
                return self.dfs_search_node_name(self.tree.root, selected_node_name)
            return self.tree.current_node.parent
        # 再看当前节点的子节点是不是
        for child in self.tree.current_node.children:
            if child.ch_name == selected_node_name:
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
        s, classify = self.init_tree()
        
        while s.lower() not in ["no", "q", "quit", "exit"]:
            
            if classify.startswith("添加"):
                # print("\n=====================\n正在执行\n=====================")
               
                # 将当前节点转换为内部节点
                self.tree.convert_leaf_to_internal(self.tree.current_node)
                print("current_node: ", self.tree.current_node.ch_name)
                # 先generate一个current_node的叶子节点，再拆解这个叶子节点
                en_name, ch_name, detailed_description= self.generate_node(s)
                self.tree.add_child(en_name, ch_name, detailed_description, '')
                self.tree.current_node = self.tree.current_node.children[-1]
                self.node_names = self.display_tree(self.tree.root, 0, False)

                # 分解需求
                children = self.decompose_requirements(self.tree.current_node.ch_name)
                children = json.loads(children)
                # 添加子节点
                for child in children:
                    self.tree.add_child(child['enName'].replace(" ",""), child['chName'], child['description'], '')

                # 显示当前树结构
                print("\n=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")
            
            elif classify.startswith("删除"):
                not_delete = [self.tree.root.ch_name]
                # 循环删除节点，直到用户确认删除
                while self.tree.current_node is not None:
                    self.display_node("您想要删除的节点信息如下所示", self.tree.current_node)
                    response = input("你确认永久删除{}吗[y]/n: ".format(self.tree.current_node.ch_name)).strip().lower()
                    if response == 'y' or response == '':
                        self.tree.remove_node()
                    else:
                        not_delete.append(self.tree.current_node.ch_name)
                    # print(not_delete)
                    # 更新树结构并显示
                    self.node_names = self.display_tree(self.tree.root, 0, False)
                    # 从self.node_names中删除not_delete
                    for node_name in not_delete:
                        if node_name in self.node_names:
                            self.node_names.remove(node_name)
                    # print(self.node_names)
                    self.tree.current_node = self.location_node(s, "delete")
                
                # 显示当前树结构
                print("\n=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")
                self.tree.current_node = self.tree.root
            
            elif classify.startswith("修改"):
                # 显示当前节点信息并询问用户需要修改成什么
                self.display_node("您想要修改的节点信息如下所示", self.tree.current_node)
                new_en_name = input(f"请输入新的英文名称，回车保留当前数据： {self.tree.current_node.en_name} ").strip() or self.tree.current_node.en_name
                new_ch_name = input(f"请输入新的中文名称，回车保留当前数据: {self.tree.current_node.ch_name} ").strip() or self.tree.current_node.ch_name
                new_description = input(f"请输入新的描述，回车保留当前数据: {self.tree.current_node.description} ").strip() or self.tree.current_node.description
                new_code = input(f"请输入新的代码，回车保留当前数据: {self.tree.current_node.code} ").strip() or self.tree.current_node.code
                new_file_path = input(f"请输入新的文件路径，回车保留当前数据: {self.tree.current_node.file_path} ").strip() or self.tree.current_node.file_path
                self.tree.modify_current_node(new_en_name, new_ch_name, new_description, new_code, new_file_path)
                
                # 显示当前树结构
                print("\n=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")
            
            elif classify.startswith("生成代码"):
                # 生成当前节点的代码
                self.tree.current_node = self.tree.root
                print("开始在目录{}生成代码...".format(self.filepath))
                self.tree.construct_current_code(self.filepath)
                # 创建文件夹和文件
                create_directory_and_files(self.tree.root.en_name, self.tree.file_node_map,self.tree.current_node, self.filepath, [])
                save_tree_to_json(self.tree, self.tree.root.en_name+"/restore.json")
                self.start_watching()
                print("=====================\n所有代码生成完毕！请在{}中查看\n=====================".format(self.filepath))
            
            elif classify.startswith("展示信息"):
                self.display_node("您想要的节点信息如下所示", self.tree.current_node)

            elif classify.startswith("拆解"):
                # print("\n=====================\n正在执行\n=====================")

                # 获取从根节点到当前节点的所有ch_name
                path = self.get_path_to_current_node()
                # 将路径信息添加到s中
                s = "从根节点到当前节点的名字依次是 " + " -> ".join(path) + " 请对 " + self.tree.current_node.ch_name +" 进行功能拆解"
                
                # 将当前节点转换为内部节点
                self.tree.convert_leaf_to_internal(self.tree.current_node)
                # 分解需求
                children = self.decompose_requirements(s)
                children = json.loads(children)
                # 添加子节点
                for child in children:
                    self.tree.add_child(child['enName'].replace(" ",""), child['chName'], child['description'], '')

                # 显示当前树结构
                print("\n=====================\n当前树结构如下：\n=====================")
                self.node_names = self.display_tree(self.tree.root)
                print("=====================")

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
                # 分类用户输入的需求
                self.tree.current_node = self.location_node(s)
                classify = self.requirements_classification(s)
                if classify.startswith("code"):
                    break
                if self.tree.current_node is None:
                    # 显示当前树结构
                    print("\n=====================\n当前树结构如下：\n=====================")
                    self.node_names = self.display_tree(self.tree.root)
                    print("=====================")
                    print("\n对不起，我无法理解您的需求，您可以在输入中指明关键词：增删改查拆分，或者输入q/quit/exit/no退出系统。")
                    s = input().strip()
                else:
                    break
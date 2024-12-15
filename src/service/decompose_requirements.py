import json
import ollama
import re
from prompt import role, task, one_shot, location_node_example, init_tree_example, process_json_example
from requirement_tree.requirement_tree import RequirementTree
from file_system.fileChange import *
from watchdog.observers import Observer
import threading
import multiprocess
from difflib import SequenceMatcher
import time
import jieba.posseg as pseg
from datetime import datetime
import sys, os
from process_tree import *
sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
from get_config import read_config

class RequirementManager:
    def __init__(self, filepath):
        self.tree = None
        self.node_names = []
        self.filepath = filepath

    def requirements_classification(self, s: str) -> str:
        """
        将用户输入的需求分类
        """

        # 先用规则识别一层
        act_list = {
            "细化": "拆解",
            "具体": "拆解",  # 与“细化”类似含义
            "详细说明": "拆解",
            "深入分析": "拆解",
            "笼统": "拆解",
            "概括": "拆解",  # 与“笼统”类似含义，将内容概括起来也可理解为一种拆解分析方式
            "拆解": "拆解",
            "分解": "拆解",
            "分析": "拆解",  # 对事物进行分析可类比为拆解其组成部分
            "实现": "拆解",
            "完成": "拆解",  # 完成某个功能或任务可视为对其进行拆解实现
            "执行": "拆解",
            "构建": "拆解",  # 构建某个东西可分解为多个步骤来实现，即拆解实现
            "增": "增",
            "添加": "增",
            "增加": "增",
            "补充": "增",
            "插入": "增",
            "删": "删",
            "移除": "删",
            "去掉": "删",
            "清除": "删",
            "改": "改",
            "更改": "改",
            "编辑": "改",
            "调整": "改",
            "修正": "改",
            "代码": "生成代码",
            "程序": "生成代码",  # 用户提及编写程序也可理解为生成代码
            "脚本": "生成代码",
            "算法": "生成代码",  # 涉及算法编写也是生成代码的一种
            "项目": "生成代码",
            "工程": "生成代码",  # 开发项目或工程需要生成代码
            "应用": "生成代码",  # 创建应用程序涉及代码生成
            "查": "查",
            "展示": "查",
            "呈现": "查",
            "列出": "查",
            "打印": "查",  # 在编程语境中，打印信息也是一种展示方式
            "输出": "查"  # 输出相关内容可理解为查
        }
        for act in act_list.keys():
            if act in s:
                return act_list[act]

        str_node_names=",".join(self.node_names)

        res="n"
        classification=""

        while res not in ["y", ""]:
            prompt = """你是语言专家。
            将用户需求分类到以下类别之一：增、删、改、查、拆解、生成代码。仅返回一个词。
            需求：{requirement}
            分类的目的是判断用户想要对{node_names}中的某个节点进行何种操作
            """.format(requirement=s, node_names=str_node_names)
            res = multiprocess.multiprocess_chat(model=read_config("model"), stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
            classification = res['message']['content'].lower()
            if classification not in act_list.keys():
                s = self.Rhetorical(s)
                res = "n"
                continue
            print(f"请问你是想对 {self.tree.current_node.ch_name} 进行 \"{classification}\" 操作吗？ [y]/n")
            res = input().strip().lower()
            if res == "n":
                return "自动"

        if classification in act_list.keys():
            return act_list[classification]
        else:
            return "自动"

    def decompose_requirements(self, input):
        """
        Decompose the requirements into a list of requirements.
        """
        input = "The requirement that you should decompose is:\n" + input.strip()
        if read_config("language") == "Chinese":
            input = input.strip()+"，有哪些功能\n"

        # 不对用户输入做过多处理，直接让大模型处理
        init_res=multiprocess.multiprocess_chat(
            model=read_config("model"), 
            stream=False, 
            messages=[{"role": "user", "content": self.tree.root.ch_name+"中，"+input}], 
            options={"temperature": 0},
        )
        # print("init_res: ", init_res["message"]["content"])

        print("Please wait for a moment, the system is decomposing the requirements...")
        res = multiprocess.multiprocess_chat(
            model=read_config("model"), 
            stream=False, 
            messages=[{"role": "user", "content": role + input + one_shot + "\n请参考下面的功能分解" + init_res["message"]["content"]}], 
            options={"temperature": 0},
        )
        print("The requirements have been decomposed.")
        content = res['message']['content']
        # print("content: ", content)
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

    def display_tree(self):
        """
        显示树的结构
        """

        print("\n=====================\n当前树结构如下：\n=====================")
        self.node_names = self.display_tree_dfs(self.tree.root)
        print("=====================")

    def display_tree_dfs(self, node, depth=0, display=True):
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
                node_name.extend(self.display_tree_dfs(child, depth + 1, display))
        return node_name

    def generate_code(self):
        # 生成当前节点的代码
        self.tree.current_node = self.tree.root
        print("开始在目录{}生成代码...".format(self.filepath))
        self.tree.construct_current_code(self.filepath)
        # 创建文件夹和文件
        create_directory_and_files(self.tree.root.en_name, self.tree.file_node_map,self.tree.current_node, self.filepath, [])
        save_tree_to_json(self.tree, self.tree.root.en_name+"/restore.json")
        create_requirements_txt(self.tree, self.tree.root.en_name)
        self.start_watching()
        print("=====================\n所有代码生成完毕！请在{}中查看\n=====================".format(self.filepath))

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
                        self.node_names = self.display_tree_dfs(self.tree.root)

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
                                self.node_names = self.display_tree_dfs(self.tree.root)
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
        self.node_names = self.display_tree_dfs(self.tree.root, 0, False)

        return s, "拆解"

    def decompose_node(self):
        for child in self.tree.current_node.children:
            self.tree.current_node.remove_child(child.ch_name)
        # 分解需求
        children = self.decompose_requirements(self.tree.current_node.ch_name)
        children = json.loads(children)
        # 增子节点
        for child in children:
            if child["chName"] in self.node_names:
                continue
            self.tree.add_child(child['enName'].replace(" ","").replace("-","").replace("_",""), child['chName'], child['description'], '')

    def modify_by_user(self):
        # 显示当前节点信息并询问用户需要改成什么
        self.display_node("您想要改的节点信息如下所示", self.tree.current_node)
        new_en_name = input(f"请输入新的英文名称，回车保留当前数据： {self.tree.current_node.en_name} ").strip() or self.tree.current_node.en_name
        new_ch_name = input(f"请输入新的中文名称，回车保留当前数据: {self.tree.current_node.ch_name} ").strip() or self.tree.current_node.ch_name
        new_description = input(f"请输入新的描述，回车保留当前数据: {self.tree.current_node.description} ").strip() or self.tree.current_node.description
        new_code = input(f"请输入新的代码，回车保留当前数据: {self.tree.current_node.code} ").strip() or self.tree.current_node.code
        new_file_path = input(f"请输入新的文件路径，回车保留当前数据: {self.tree.current_node.file_path} ").strip() or self.tree.current_node.file_path
        self.tree.modify_current_node(new_en_name, new_ch_name, new_description, new_code, new_file_path)
        
        # 显示当前树结构
        self.display_tree()

    # 让大模型直接处理整棵树
    def process_by_agent(self, s):
        self.tree.current_node = self.tree.root
        json_without_description = delete_description(json.dumps(self.tree.to_dict()))

        flag=True
        while flag:
            flag=False
            # print("json.dumps(self.tree.to_dict()): ", json.dumps(self.tree.to_dict()))
            # 生成对话提示
            prompt = f"你是一位专业的 JSON 专家。\n\
            用户需求：我想要{s}\n\
            请基于用户需求修改JSON，返回的JSON里面的对象属性必须完全包含{",".join(self.node_names)}\n\
            当前JSON如下：\n{json_without_description}\n\
            例子：{process_json_example}"

            # 调用大模型生成响应
            res = multiprocess.multiprocess_chat(model=read_config("model"), stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})

            # 提取生成的文本
            refined_requirements = res['message']['content'].strip()

            # 使用正则表达式提取 JSON 内容
            pattern = re.compile(r"```json(.*?)```", re.DOTALL)
            matches = pattern.findall(refined_requirements)
            if not matches:
                flag=True

            # 解析 JSON 并重新构建 self.root
            updated_tree_info = json.loads(matches[0].strip())
            try:
                self.tree.root = self.tree.build_tree_from_dict(updated_tree_info)
            except Exception as e:
                flag=True

        # 显示当前树结构
        self.display_tree()

    def modify_by_agent(self, s):
        current_info = {
            "en_name": self.tree.current_node.en_name,
            "ch_name": self.tree.current_node.ch_name,
            "description": self.tree.current_node.description,
            "code": self.tree.current_node.code,
            "file_path": self.tree.current_node.file_path
        }
        prompt = f"当前节点信息如下：\n{json.dumps(current_info, ensure_ascii=False, indent=4)}\n\n用户输入：{s}\n请基于用户输入更新节点信息，并以JSON格式输出。"

        while True:
            # 调用大模型生成响应
            res = multiprocess.multiprocess_chat(format="json" ,model=read_config("model"), stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})

            # 提取生成的文本并解析为JSON
            try:
                updated_info = json.loads(res['message']['content'].strip())
                break
            except Exception as e:
                pass

        # 更新节点信息
        new_en_name = updated_info.get("en_name", self.tree.current_node.en_name)
        new_ch_name = updated_info.get("ch_name", self.tree.current_node.ch_name)
        new_description = updated_info.get("description", self.tree.current_node.description)
        new_code = updated_info.get("code", self.tree.current_node.code)
        new_file_path = updated_info.get("file_path", self.tree.current_node.file_path)
        self.tree.modify_current_node(new_en_name, new_ch_name, new_description, new_code, new_file_path)

        # 拆解改后的需求
        self.decompose_node()
        
        # 显示当前树结构
        self.display_tree()

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
        res = multiprocess.multiprocess_chat(model=read_config("model"), stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        description = res['message']['content'].strip()
        lines = description.split('\n')

        for i in range(len(lines)):
            if "en_name" in lines[i]:
                en_name = re.sub(r'[^a-zA-Z]', '', lines[i].split(":")[1].strip().replace(" ","").replace("-","").replace("_",""))
            elif "ch_name" in lines[i]:
                ch_name = lines[i].split(":")[1].strip()
            elif "description" in lines[i]:
                detailed_description = "\n".join(lines[i+1:]).strip()
                break
        return en_name, ch_name, detailed_description

    def Rhetorical(self, s):
        # 生成对话提示
        prompt = f"用户的问题是：{s}\n请向用户提问，进一步精细化需求。"

        # 调用大模型生成响应
        res = multiprocess.multiprocess_chat(model=read_config("model"), stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})

        # 提取生成的文本
        refined_requirements = res['message']['content'].lower()

        return refined_requirements

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
        启动文件监听器，监听指定目录中的文件改事件。
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

        # add locating with rules
        for node_name in self.node_names:
            if node_name in s:
                return self.dfs_search_node_name(self.tree.root, node_name)

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
            # print("prompt: ", prompt)

            res = multiprocess.multiprocess_chat(model=read_config("model"), stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
            selected_node_name = res['message']['content'].strip()

            # print(f"=====================\n筛选前：{selected_node_name}\n=====================")

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
            
            if classify.startswith("增"):
                # print("\n=====================\n正在执行\n=====================")
               
                # 将当前节点转换为内部节点
                self.tree.convert_leaf_to_internal(self.tree.current_node)
                # print("current_node: ", self.tree.current_node.ch_name)
                # 先generate一个current_node的叶子节点，再拆解这个叶子节点
                en_name, ch_name, detailed_description= self.generate_node(s)
                self.tree.add_child(en_name, ch_name, detailed_description, '')
                self.tree.current_node = self.tree.current_node.children[-1]
                self.node_names = self.display_tree_dfs(self.tree.root, 0, False)

                # 分解需求
                self.decompose_node()

                # 显示当前树结构
                self.display_tree()
            
            elif classify.startswith("删"):
                not_delete = [self.tree.root.ch_name]
                # 循环删节点，直到用户确认删
                while self.tree.current_node is not None:
                    self.display_node("您想要删的节点信息如下所示", self.tree.current_node)
                    response = input("你确认永久删{}吗[y]/n: ".format(self.tree.current_node.ch_name)).strip().lower()
                    if response == 'y' or response == '':
                        self.tree.remove_node()
                    else:
                        not_delete.append(self.tree.current_node.ch_name)
                    # print(not_delete)
                    # 更新树结构并显示
                    self.node_names = self.display_tree_dfs(self.tree.root, 0, False)
                    # 从self.node_names中删not_delete
                    for node_name in not_delete:
                        if node_name in self.node_names:
                            self.node_names.remove(node_name)
                    # print(self.node_names)
                    self.tree.current_node = self.location_node(s, "delete")
                
                # 显示当前树结构
                self.display_tree()
                self.tree.current_node = self.tree.root
            
            elif classify.startswith("改"):
                # self.modify_by_user()
                self.modify_by_agent(s)
            
            elif classify.startswith("生成代码"):
                self.generate_code()
            
            elif classify.startswith("查"):
                self.display_node("您想要的节点信息如下所示", self.tree.current_node)

            elif classify.startswith("拆解"):
                # print("\n=====================\n正在执行\n=====================")

                # 获取从根节点到当前节点的所有ch_name
                path = self.get_path_to_current_node()
                # 将路径信息增到s中
                s = "从根节点到当前节点的名字依次是 " + " -> ".join(path) + " 请对 " + self.tree.current_node.ch_name +" 进行功能拆解"
                
                # 将当前节点转换为内部节点
                self.tree.convert_leaf_to_internal(self.tree.current_node)

                # 分解需求
                self.decompose_node()

                # 显示当前树结构
                self.display_tree()

            elif classify.startswith("自动"):
                self.process_by_agent(s)

            else:
                # 显示当前树结构
                self.display_tree()
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
                    self.node_names = self.display_tree_dfs(self.tree.root)
                    print("=====================")
                    print("\n对不起，我无法理解您的需求，您可以在输入中指明关键词：增删改查拆分，或者输入q/quit/exit/no退出系统。")
                    s = input().strip()
                else:
                    break

    def agent_interaction(self):
        """
        用户交互函数，用于处理用户输入的需求并对需求树进行相应的操作。
        """
        # 初始化根节点
        s, classify = self.init_tree()
        s = self.agent_imitate_user()
        
        while s.lower() not in ["no", "q", "quit", "exit"]:
            
            if classify.startswith("增"):
                # print("\n=====================\n正在执行\n=====================")
               
                # 将当前节点转换为内部节点
                self.tree.convert_leaf_to_internal(self.tree.current_node)
                print("current_node: ", self.tree.current_node.ch_name)
                # 先generate一个current_node的叶子节点，再拆解这个叶子节点
                en_name, ch_name, detailed_description= self.generate_node(s)
                if ch_name not in self.node_names:
                    self.tree.add_child(en_name, ch_name, detailed_description, '')
                    self.tree.current_node = self.tree.current_node.children[-1]
                    self.node_names = self.display_tree_dfs(self.tree.root, 0, False)

                # 分解需求
                self.decompose_node()

                # 显示当前树结构
                self.display_tree()
            
            elif classify.startswith("删"):
                not_delete = [self.tree.root.ch_name]
                # 循环删节点，直到用户确认删
                while self.tree.current_node is not None:
                    self.display_node("您想要删的节点信息如下所示", self.tree.current_node)
                    response = input("你确认永久删{}吗[y]/n: ".format(self.tree.current_node.ch_name)).strip().lower()
                    if response == 'y' or response == '':
                        self.tree.remove_node()
                        break
                    else:
                        not_delete.append(self.tree.current_node.ch_name)
                    # print(not_delete)
                    # 更新树结构并显示
                    self.node_names = self.display_tree_dfs(self.tree.root, 0, False)
                    # 从self.node_names中删not_delete
                    for node_name in not_delete:
                        if node_name in self.node_names:
                            self.node_names.remove(node_name)
                    # print(self.node_names)
                    self.tree.current_node = self.location_node(s, "delete")
                
                # 显示当前树结构
                self.display_tree()
                self.tree.current_node = self.tree.root
            
            elif classify.startswith("改"):
                self.modify_by_user()
            
            elif classify.startswith("生成代码"):
                self.generate_code()
            
            elif classify.startswith("查"):
                self.display_node("您想要的节点信息如下所示", self.tree.current_node)

            elif classify.startswith("拆解"):
                # print("\n=====================\n正在执行\n=====================")

                # 获取从根节点到当前节点的所有ch_name
                path = self.get_path_to_current_node()
                # 将路径信息增到s中
                s = "从根节点到当前节点的名字依次是 " + " -> ".join(path) + " 请对 " + self.tree.current_node.ch_name +" 进行功能拆解"
                
                # 将当前节点转换为内部节点
                self.tree.convert_leaf_to_internal(self.tree.current_node)
                # 分解需求
                self.decompose_node()

                # 显示当前树结构
                self.display_tree()
            
            elif classify.startswith("自动"):
                self.process_by_agent(s)

            else:
                # 显示当前树结构
                self.display_tree()
                print("对不起，我无法理解您的需求，请基于树结构详细描述您的需求。")
            
            # 询问用户是否有进一步的需求
            print("\n请问您有什么进一步的需求？输入q/quit/exit/no退出系统。")
            s = self.agent_imitate_user()
            print("s: ", s)
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
                    self.node_names = self.display_tree_dfs(self.tree.root)
                    print("=====================")
                    print("\n对不起，我无法理解您的需求，您可以在输入中指明关键词：增删改查拆分，或者输入q/quit/exit/no退出系统。")
                    s = self.agent_imitate_user()
                else:
                    break

    def agent_imitate_user(self):
        # 获取当前时间并格式化为字符串
        current_time = datetime.now().strftime("%Y%m%d_%H")

        # 使用当前时间作为日志文件名
        log_filename = os.path.join(os.path.dirname(__file__), "log/{}.log".format(current_time))
            
        with open(log_filename, "r") as f:
            history = f.read()
        
        prompt="你需要模拟一个想要实现学生管理系统的用户，请提出一个具体的需求。\
            下面是你的对话历史: {history}。\
            例子输出：我想要增注册功能\
        ".format(history=history)

        res = multiprocess.multiprocess_chat(model=read_config("model"), stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        output = res['message']['content'].lower()
        
        # 将output写入log文件
        with open(log_filename, "a") as f:
            f.write(output + "\n")
        return output

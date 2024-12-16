import multiprocessing.connection
import sys, os
sys.path.append(os.path.dirname(__file__))
import multiprocess.background
import requirement_tree_node as rtn
import requirement_tree_visitor as rtv
import ollama
import json
import multiprocessing
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
import multiprocess
sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
from get_config import read_config


def do_change_tree(func):
    def wrapper(self: 'RequirementTree', *args, **kwargs):
        result = func(self, *args, **kwargs)

        # generate at background
        if self.conn is not None:
            try:
                self.conn.send('stop')
                self.conn.close()
            except BrokenPipeError:
                pass
            self.conn = None
        conn1, conn2 = multiprocessing.Pipe()
        background = multiprocessing.Process(target=multiprocess.background.generate_code, args=(conn1, self))
        background.start()
        self.conn = conn2

        return result
    return wrapper


class RequirementTree:
    def __init__(self, project_en_name: str='', project_ch_name: str='', project_description: str='', file_path: str=''):
        """
        接口1: 创建一棵空树
        @param file_path: 在插件里才能用到，目前直接传入空字符串
        """
        self.root = rtn.RequirementInternalNode(project_en_name, project_ch_name, project_description, file_path)
        self.current_node = self.root
        self.file_node_map = {}
        self.conn: multiprocessing.connection.Connection = None

    def get_current_node(self):
        return self.current_node

    @do_change_tree
    def add_child(self, child_en_name: str, child_ch_name, child_description: str, file_path: str=''):
        """
        接口3.1: 给当前节点添加子节点
        @param file_path: 在插件里才能用到，目前直接传入空字符串
        @return: 返回新添加的节点
        """
        for child in self.current_node.children:
            if child.en_name == child_en_name:
                return None
        child = rtn.RequirementInternalNode(child_en_name, child_ch_name, child_description, file_path)
        self.current_node.add_child(child)
        return child
    
    @do_change_tree
    def remove_child(self, child_name: str) -> bool:
        """
        接口3.2: 给当前节点删除子节点
        @return: 是否删除成功
        """
        return self.current_node.remove_child(child_name)
    
    @do_change_tree
    def remove_node(self) -> bool:
        """
        接口3.3: 删除当前节点
        @return: 是否删除成功
        """
        parent = self.current_node.parent
        if parent is None:
            return False
        return_value=parent.remove_child(self.current_node.ch_name)
        self.current_node=parent
        return return_value
    
    def get_child_with_name(self, child_name: str):
        """
        获取当前节点名为 child_name 的子节点，不存在时返回 None
        """
        for child in self.current_node.children:
            if child.en_name == child_name:
                return child
        return None

    def move_current_node(self, up: bool, child_name: str = None):
        """
        接口4: 移动当前节点
        @param up: 为True时移动到父节点，child_name不需要传入；
                   为False时，移动到名为child_name的子节点
        @return: 移动后的当前节点
        """
        if up:
            if self.current_node.parent is not None:
                self.current_node = self.current_node.parent
            else:
                raise KeyError
        else:
            child = self.get_child_with_name(child_name)
            if child is not None:
                self.current_node = child
            else:
                raise KeyError
        return self.current_node
    
    @do_change_tree
    def modify_current_node(self, new_en_name=None, new_ch_name=None, new_description=None, new_code=None, new_file_path=None):
        """
        接口5: 修改当前节点
        不需要修改的信息直接传None，或者不传
        """
        # TODO: 这里可能需要向上或者向下传播一下更新

        if new_en_name is not None:
            self.current_node.en_name = new_en_name
        if new_ch_name is not None:
            self.current_node.ch_name = new_ch_name
        if new_description is not None:
            self.current_node.description = new_description
        if new_code is not None:
            self.current_node.code = new_code
        if new_file_path is not None:
            self.current_node.file_path = new_file_path

    def construct_current_code(self, filepath,callback=None) -> str:
        """
        接口6: 生成当前节点的代码
        @param callback: 暂时不用传，考虑到模型可能会修改子模块，我们需要用户确认这些修改，所以要添加一个callback获取用户反馈。但目前还不支持这样的功能
        @return: 返回当前节点的代码
        """
        # TODO: 添加用户反馈

        # # 如果当前节点是叶子节点，转换为叶子节点
        # if len(self.current_node.children) == 0:
        #     parent: rtn.RequirementInternalNode = self.current_node.parent
        #     leaf = self.current_node.convert_to_leaf_node()
        #     parent.remove_child(leaf.en_name)
        #     parent.add_child(leaf)
        #     self.current_node = leaf

        # # 生成代码
        # self.current_node.construct_code()
        print('等待背景进程返回生成结果')
        tree: RequirementTree = self.conn.recv()
        print('接收到背景进程生成结果')
        copy_visitor = rtv.CopyCodeVisitor(tree)
        self.current_node.accept(copy_visitor)

        return self.current_node.code

    def convert_leaf_to_internal(self, leaf_node):
        """
        接口7: 将叶子结点转换为内部结点
        @param leaf_node: 要转换的叶子结点
        @description: 
            如果传入的节点已经是内部结点，则不进行任何操作。
            否则，会创建一个新的内部结点，并将其替换为原来的叶子结点。如果叶子结点有父节点，
            则会在父节点中进行替换操作。最后，将当前节点更新为新的内部结点。
        """
        if type(leaf_node) == rtn.RequirementInternalNode:
            return
        new_internal_node = rtn.RequirementInternalNode(leaf_node.en_name, leaf_node.ch_name, "新的描述（反映中间节点功能）", leaf_node.file_path, [])
        if leaf_node.parent:
            parent_node = leaf_node.parent
            parent_node.remove_child(leaf_node)
            parent_node.add_child(new_internal_node)
        self.current_node = new_internal_node

    def build_tree_from_dict(self, tree_dict):
        # 接口8: 基于json递归构建树
        node = rtn.RequirementInternalNode(
            tree_dict['en_name'],
            tree_dict['ch_name'],
            tree_dict['description'],
            tree_dict.get('file_path', '')
        )
        for child_dict in tree_dict.get('children', []):
            child_node = self.build_tree_from_dict(child_dict)
            node.add_child(child_node)
        self.file_node_map[tree_dict.get('file_path', '')] = node
        return node

    def to_dict(self):
        """
        把当前节点对应的子树转换成dict格式
        """
        to_dict_visitor = rtv.ConvertToDictVisitor()
        return self.current_node.accept(to_dict_visitor)

    def generate_dependencies(self):
        prompt="""
        You are a top-notch Python programmer. 
        You are presented with a tree-structured requirement in the form of json, where the funtion of a node is composed of its child nodes.
        You are responsible to explore the functionalities and identify the dependencies between the nodes of the tree and output them in the form of array json.
        Output Example:
        [[Frontend, Add], [Frontend, Subtract]]
        which means Frontend Module is dependent on both Add and Subtract Module.
        Only output the dependencies which cannot derive from the tree structure, i.e. non parent-child dependencies.

        The given requirement tree is:
        {tree}

        Your output (only the json, no additional response):
        """.format(tree=json.dumps(self.to_dict()))
        print(json.dumps(self.to_dict()))
        if read_config("language")=="Chinese":
            prompt="""
            你是一位顶尖的Python程序员。
            你被赋予了一个树形结构的需求，其中每个节点的功能由其子节点组成。
            你的任务是探索功能并识别树的节点之间的依赖关系，并以数组json的形式输出。
            输出示例：
            [[前端，加法]，[后端，减法]]
            这意味着前端模块依赖于加法和减法模块。
            只输出不能从树结构推导出的依赖关系，即非父子依赖关系。

            给定的需求树是：
            {tree}

            你的输出（只有json，没有额外的回复）
            """.format(tree=json.dumps(self.to_dict()))
        res = multiprocess.multiprocess_chat(model=read_config("model"), stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        print(res['message']['content'])

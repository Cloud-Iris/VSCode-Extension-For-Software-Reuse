import ollama
import requirement_tree.requirement_tree_node as rtn
from requirement_tree.requirement_tree_visitor import extract_new_implementation_from_response
import os

class RequirementTree:
    def __init__(self, project_en_name: str='', project_ch_name: str='', project_description: str='', file_path: str=''):
        """
        接口1: 创建一棵空树
        @param file_path: 在插件里才能用到，目前直接传入空字符串
        """
        self.root = rtn.RequirementInternalNode(project_en_name, project_ch_name, project_description, file_path)
        self.current_node = self.root

    def get_current_node(self) -> rtn.RequirementTreeNode:
        return self.current_node

    def add_child(self, child_en_name: str, child_ch_name, child_description: str, file_path: str) -> rtn.RequirementTreeNode:
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
    
    def remove_child(self, child_name: str) -> bool:
        """
        接口3.2: 给当前节点删除子节点
        @return: 是否删除成功
        """
        return self.current_node.remove_child(child_name)
    
    def get_child_with_name(self, child_name: str) -> rtn.RequirementTreeNode:
        """
        获取当前节点名为 child_name 的子节点，不存在时返回 None
        """
        for child in self.current_node.children:
            if child.en_name == child_name:
                return child
        return None

    def move_current_node(self, up: bool, child_name: str = None) -> rtn.RequirementTreeNode:
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
            child = self.get_child_with_name(child_name)
            if child is not None:
                self.current_node = child
        return self.current_node
    
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

    def construct_current_code(self, callback=None) -> str:
        """
        接口6: 生成当前节点的代码
        @param callback: 暂时不用传，考虑到模型可能会修改子模块，我们需要用户确认这些修改，所以要添加一个callback获取用户反馈。但目前还不支持这样的功能
        @return: 返回当前节点的代码
        """
        # TODO: 添加用户反馈

        def create_directory_and_files(node, path, imports):
            """
            递归创建文件夹和文件
            @param node: 当前节点
            @param path: 当前路径
            @param imports: 导入语句列表
            """
            # 创建当前节点的文件夹
            current_path = os.path.join(path, node.en_name)
            os.makedirs(current_path, exist_ok=True)

            # 如果是叶子节点，创建文件
            if len(node.children) == 0:
                file_path = os.path.join(current_path, f"{node.en_name}.py")
                with open(file_path, 'w') as file:
                    file.write(node.code)
                return

            # 递归处理子节点
            for child in node.children:
                create_directory_and_files(child, current_path, imports)
                # 添加导入语句
                imports.append(f"from {child.en_name}.{child.en_name} import *")

            # 回溯时创建当前节点的文件
            file_path = os.path.join(current_path, f"{node.en_name}.py")
            with open(file_path, 'w') as file:
                # 写入导入语句
                file.write("\n".join(imports) + "\n\n")
                file.write(node.code)

        # 如果当前节点是叶子节点，转换为叶子节点
        if len(self.current_node.children) == 0:
            parent: rtn.RequirementInternalNode = self.current_node.parent
            leaf = self.current_node.convert_to_leaf_node()
            parent.remove_child(leaf.en_name)
            parent.add_child(leaf)
            self.current_node = leaf

        # 生成代码
        self.current_node.construct_code()

        # 创建文件夹和文件
        create_directory_and_files(self.current_node, os.getcwd(), [])

        return self.current_node.code

    def convert_leaf_to_internal(self, leaf_node: rtn.RequirementLeafNode):
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


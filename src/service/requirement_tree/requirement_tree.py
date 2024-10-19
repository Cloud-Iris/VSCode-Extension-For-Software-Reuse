import requirement_tree_node as rtn


class RequirementTree:
    def __init__(self, project_name: str, project_description: str, file_path: str):
        """
        接口1: 创建一棵空树
        @param file_path: 在插件里才能用到，目前直接传入空字符串
        """
        self.root = rtn.RequirementInternalNode(project_name, '', project_description, file_path)
        self.current_node = self.root

    def get_current_node(self) -> rtn.RequirementTreeNode:
        return self.current_node

    def add_child(self, child_name: str, child_description: str, file_path: str) -> rtn.RequirementTreeNode:
        """
        接口3.1: 给当前节点添加子节点
        @param file_path: 在插件里才能用到，目前直接传入空字符串
        @return: 返回新添加的节点
        """
        child = rtn.RequirementInternalNode(child_name, '', child_description, file_path)
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
    
    def modify_current_node(self, new_name=None, new_description=None, new_code=None, new_file_path=None):
        """
        接口5: 修改当前节点
        不需要修改的信息直接传None，或者不传
        """
        # TODO: 这里可能需要向上或者向下传播一下更新

        if new_name is not None:
            self.current_node.en_name = new_name
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

        if(len(self.current_node.children) == 0):
            # 应该是一个叶子结点
            parent: rtn.RequirementInternalNode = self.current_node.parent
            leaf = self.current_node.convert_to_leaf_node()
            parent.remove_child(leaf.en_name)
            parent.add_child(leaf)
            self.current_node = leaf
        self.current_node.construct_code()
        return self.current_node.code



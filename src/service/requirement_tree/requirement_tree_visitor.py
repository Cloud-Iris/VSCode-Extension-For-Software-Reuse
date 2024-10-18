from service.requirement_tree.requirement_tree_node import RequirementTreeNode, RequirementInternalNode, RequirementLeafNode


class RequirementTreeVisitorBase:
    def __init__(self):
        pass

    def visit_internal(self, node: RequirementInternalNode):
        pass
    
    def visit_leaf(self, node: RequirementLeafNode):
        pass


class AddInterfaceVisitor(RequirementTreeVisitorBase):
    def __init__(self, requirement: str):
        self.requirement = requirement
    
    def visit_leaf(self, node: RequirementTreeNode):
        # TODO: 调用大模型，修改子节点的代码
        # node.code = ollama.chat(.......)
        pass
    
    def visit_internal(self, node: RequirementInternalNode):
        # TODO: 内部节点可能也无法满足其父节点的要求，可能要递归地要求做子节点修改
        # 检查当前节点是否可以满足父节点的要求
        # satisfiable = ollama.chat(......)
        satisfiable = True
        if not satisfiable: # 递归地让子节点作出修改
            # TODO: 这里把父节点的需求做一下转变
            # node_requirement = ollama.chat(......, self.requirement)
            node_requirement = self.requirement
            node.require_child_add_interface(node_requirement)

        # TODO: 子节点不需要修改，或者已经修改好了，再来修改node
        # node.code = ollama.chat(....)
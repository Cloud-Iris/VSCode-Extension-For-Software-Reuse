import uuid
import sys, os
sys.path.append(os.path.dirname(__file__))
import requirement_tree_visitor as rtv
import ollama

# 假设需求树上的每个节点都对应一个类，每个内部节点需要调用子节点的接口、生成额外的代码来组合子节点的功能。
# 有时子节点提供的接口不能满足父节点的组合需求，这时候父节点需要要求子节点添加相应的接口


class RequirementTreeNode:
    def __init__(self, en_name: str, ch_name:str, description: str, file_path: str):
        self.en_name = en_name
        self.ch_name = ch_name
        self.description = description
        self.file_path = file_path
        self.parent = None
        self.code = ""
        self.id = uuid.uuid4()
    
    # 访问者模式
    def accept(self, visitor):
        pass

    # 根据子节点和需求来构建当前节点的代码
    def construct_code(self):
        visitor = rtv.ConstructCodeVisitor()
        self.accept(visitor)

# 叶子结点需要存储当前最小模块的实现代码
class RequirementLeafNode(RequirementTreeNode):
    def __init__(self, en_name: str, ch_name: str, description: str, file_path: str):
        super().__init__(en_name, ch_name, description, file_path)
    
    def accept(self, visitor):
        return visitor.visit_leaf(self)
    
    def __str__(self):
        return f'name: {self.en_name}, parent: {self.parent.en_name if self.parent is not None else "None"}, description: {self.description}, code: {self.code}'


# 内部节点负责组合子节点的功能
class RequirementInternalNode(RequirementTreeNode):
    def __init__(self, en_name: str, ch_name: str, description: str, file_path: str):
        super().__init__(en_name, ch_name, description, file_path)
        self.children = []
    
    def accept(self, visitor):
        return visitor.visit_internal(self)
    
    def add_child(self, child: RequirementTreeNode):
        self.children.append(child)
        child.parent = self
    
    def remove_child(self, child_name: str) -> bool:
        for i in range(0, len(self.children)):
            if self.children[i].en_name == child_name or self.children[i].ch_name == child_name:
                self.children[i].parent = None
                self.children = self.children[: i] + self.children[i + 1: ]
                return True
        return False
    
    # 当前节点不能通过子节点已有的接口来组合子节点
    def require_child_add_interface(self, requirement: str, child: RequirementTreeNode = None):
        visitor = rtv.AddInterfaceVisitor(requirement)
        if child is None:
            for child_ in self.children:
                child_.accept(visitor)
        else:
            child.accept(visitor)
    
    def convert_to_leaf_node(self) -> RequirementLeafNode:
        assert(len(self.children) == 0)
        leaf = RequirementLeafNode(self.en_name, self.ch_name, self.description, self.file_path)
        return leaf

    def __str__(self):
        return f'name: {self.en_name}, parent: {self.parent.en_name if self.parent is not None else "None"}, children: {self.children}, description: {self.description}, code: {self.code}'


    



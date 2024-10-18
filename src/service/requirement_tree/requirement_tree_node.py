import uuid
import requirement_tree_visitor as rtv

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
    def construct_code(self, requirement: str):
        pass


# 内部节点负责组合子节点的功能
class RequirementInternalNode(RequirementTreeNode):
    def __init__(self, en_name: str, ch_name: str, description: str, file_path: str, children: list[RequirementTreeNode] = []):
        super().__init__(en_name, ch_name, description, file_path)
        self.children = children
        for child in self.children:
            child.parent = self
    
    def accept(self, visitor):
        return visitor.visit_internal(self)
    
    def add_child(self, child: RequirementTreeNode):
        self.children.append(child)
        child.parent = self
    
    # 当前节点不能通过子节点已有的接口来组合子节点
    def require_child_add_interface(self, requirement: str, child: RequirementTreeNode = None):
        visitor = rtv.AddInterfaceVisitor(requirement)
        if child is None:
            for child_ in self.children:
                child_.accept(visitor)
        else:
            child.accept(visitor)
    
    # 根据子节点的代码和当前节点的需求，构建当前节点的代码
    def construct_code(self, requirement):
        context = ""
        for child in self.children:
            context += child.code # TODO: 这里context需要其他的表示形式
        context += requirement # TODO: 修改context的形式
        # TODO: 调用LLM生成代码
        # self.code = ollama.chat(context ....)


# 叶子结点需要存储当前最小模块的实现代码
class RequirementLeafNode(RequirementTreeNode):
    def __init__(self, en_name: str, ch_name: str, description: str, file_path: str):
        super().__init__(en_name, ch_name, description, file_path)
    
    def accept(self, visitor):
        return visitor.visit_leaf(self)
    
    def construct_code(self, requirement):
        context = requirement
        # TODO: 调用LLM生成叶子结点的代码
        # self.code = ollama.chat(context)
        



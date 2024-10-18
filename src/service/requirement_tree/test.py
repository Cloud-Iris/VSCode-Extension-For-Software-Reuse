from requirement_tree_node import RequirementTreeNode, RequirementInternalNode, RequirementLeafNode
if __name__ == '__main__':
    root = RequirementInternalNode('Calculator', '计算器', '实现一个计算器，支持加减乘除功能', '文件路径')
    son1 = RequirementLeafNode('AddOperation', '加法功能', '实现计算器的加法', 'leaf')
    root.add_child(son1)
    son1.code = """
        class AddOperation:
            @classmethod
            def add(a, b):
                return a + b
    """
    root.require_child_add_interface('实现减法功能', root)

    print(root.code)
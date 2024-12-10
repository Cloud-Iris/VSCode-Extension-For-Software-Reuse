from requirement_tree_node import RequirementTreeNode, RequirementInternalNode, RequirementLeafNode
from requirement_tree import RequirementTree

def test_add_interface():
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


def test_construct_code():
    root = RequirementInternalNode('Calculator', '计算器', '实现一个计算器，支持加减乘除功能', '文件路径')
    son1 = RequirementLeafNode('AddOperation', '加法功能', '实现计算器的加法', 'leaf')
    son2 = RequirementLeafNode('SubtractOperation', '减法功能', '实现计算器的减法', 'leaf')
    son3 = RequirementLeafNode('MultiplyOperation', '乘法功能', '实现计算器的乘法', 'leaf')
    son4 = RequirementLeafNode('DivideOperation', '除法功能', '实现计算器的除法', 'leaf')
    root.add_child(son1)
    root.add_child(son2)
    root.add_child(son3)
    root.add_child(son4)
    root.construct_code()
    for child in root.children:
        print(child.code)
        print('\n')
    print(root.code)


def test_requirement_tree():
    # 接口1
    tree = RequirementTree('Calculator', 'Implement a calculator, supporting add, subtract, multiply and divide.', '')

    # 接口3
    add = tree.add_child('AddOperation', '','Implement the add operation of a calculator')
    sub = tree.add_child('SubtractOperation', '','Implement the subtract operation of a calculator')
    mul = tree.add_child('MultiplyOperation', '','Implement the multiply operation of a calculator')
    div = tree.add_child('DivideOperation', '','Implement the divide operation of a calculator')
    front = tree.add_child('FrontEnd', '', 'Display GUI for all operations', '')
    store = tree.add_child('History', '', 'Result history, support query and store', '')    

    tree.generate_dependencies()


if __name__ == '__main__':
    test_requirement_tree()



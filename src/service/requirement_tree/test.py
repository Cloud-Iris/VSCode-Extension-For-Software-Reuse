from requirement_tree_node import RequirementTreeNode, RequirementInternalNode, RequirementLeafNode
if __name__ == '__main__':
    root = RequirementInternalNode('root', '根节点', '根节点的描述', '文件路径')
    son1 = RequirementLeafNode('leaf', 'leaf', 'leaf', 'leaf')
    root.add_child(son1)
    root.require_child_add_interface('1111', son1)
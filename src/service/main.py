from decompose_requirements import decompose_requirements, requirements_classification
if __name__ == "__main__":
    print("请输入您的需求：")
    s = input()
    s = requirements_classification(s)
    print(s)
    # e.g. create: 我想要创建一个计算器
    # 要和创建其他节点区分开，因为可能会有不同系统
    if s.startswith("create"):
        decompose_requirements("requirements")
    # e.g. add: 我想要添加所有的计算功能
    # e.g. add: 我想要在加法里面添加二进制加法功能
    if s.startswith("add"):
        # To Do: 
        pass
    # e.g. delete: 我想要删除加法功能
    if s.startswith("delete"):
        # To Do: 
        pass
    # e.g. modify: 我想要把加法功能修改成减法功能
    if s.startswith("modify"):
        # To Do: 
        pass
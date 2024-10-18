from decompose_requirements import decompose_requirements
if __name__ == "__main__":
    s=input()
    # e.g. create: 我想要创建一个计算器
    # 要和创建其他节点区分开，因为可能会有不同系统
    if s.beginswith("create"):
        decompose_requirements("requirements")
    # e.g. add: 我想要添加所有的计算功能
    # e.g. add: 我想要在加法里面添加二进制加法功能
    if s.beginswith("add"):
        # To Do: 
        pass
    # e.g. add: 我想要删除加法功能
    if s.beginswith("delete"):
        # To Do: 
        pass
    # e.g. add: 我想要把加法功能修改成减法功能
    if s.beginswith("modify"):
        # To Do: 
        pass
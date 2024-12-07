from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requirement_tree_node import RequirementTreeNode, RequirementInternalNode, RequirementLeafNode

import ollama
import json
import re

class RequirementTreeVisitorBase:
    def __init__(self):
        pass

    def visit_internal(self, node: 'RequirementInternalNode'):
        pass
    
    def visit_leaf(self, node: 'RequirementLeafNode'):
        pass


def extract_new_implementation_from_response(response: str) -> str:
    print("response: ", response)
    matches = re.findall(r'```Python(.*?)```', response, re.DOTALL | re.IGNORECASE)
    if(len(matches) < 1):
        matches = re.findall(r'```(.*?)```', response, re.DOTALL)
    return matches[0].strip()


def extract_submodule_codes(node: 'RequirementInternalNode') -> str:
    sub_modules = []
    for child in node.children:
        sub_modules.append({
            # "module_name": child.en_name,
            "module_code": child.code
        })
    return json.dumps(sub_modules)


def extract_satisfiability_from_response(response: str) -> bool:
    # TODO: 这里可能需要根据具体的情况做分析
    return not response.startswith('No')


def extract_child_requirement_from_response(response: str) -> str:
    # TODO: 这里把父节点的需求做一下转变
    return re.findall(r'No, I need (.*?)', response)[0].strip()


class AddInterfaceVisitor(RequirementTreeVisitorBase):
    def __init__(self, requirement: str):
        self.requirement = requirement
    
    def visit_leaf(self, node: 'RequirementTreeNode'):
        # 调用大模型，基于self.requirement修改子节点的代码
        prompt="""
        You are a top-notch Python programmer. 
        For the following requirement: {requirement}. 
        
        Refactor the provided code to be more optimized and maintainable: {code}

        Incorporate best practices and add comments where necessary. 
        Present only the refactored code.
        """.format(requirement=self.requirement,code=node.code)
        res = ollama.chat(model="qwen2.5-coder:7b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        node.code = extract_new_implementation_from_response(res['message']['content'])
    
    def visit_internal(self, node: 'RequirementInternalNode'):
        
        prompt = """
        You are a top-notch Python programmer. 
        You have already written the following code: {code}
        Now you have to refactor the code and provide more interfaces to satisfy the following requirement: {requirement}.
        What you can do is to call the interfaces provided by the following submodules.
        {sub_module_codes}
        If the interface you need was not provided by the submodule, please let me know what kind of interface you actually need.        

        Incorporate best practices and add comments where necessary. 
        If the submodules satisfy your need, present only the refactored code. Otherwise, reply 'No, I need ...' and your requirement.
        """.format(requirement=self.requirement, code=node.code, sub_module_codes=extract_submodule_codes(node))

        res = ollama.chat(model="qwen2.5-coder:7b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})

        satisfiable = extract_satisfiability_from_response(res['message']['content'])

        if not satisfiable: # 递归地让子节点作出修改
            node_requirement = extract_child_requirement_from_response(res['message']['content'])
            node.require_child_add_interface(node_requirement)
            # 现在子节点修理好了，再重新调用一遍
            node.accept(self)
        else:
            # 子节点不需要修改
            node.code = extract_new_implementation_from_response(res['message']['content'])


class ConstructCodeVisitor(RequirementTreeVisitorBase):
    def visit_leaf(self, node: 'RequirementLeafNode'):
        prompt="""
        You are a top-notch Python programmer. 
        For the following requirement: {requirement}. 
        Write a python class called {name} to satisfy the requirement.
        请封装一些模块。
        Incorporate best practices and add comments where necessary. 
        """.format(name=node.en_name, requirement=node.description)
        res = ollama.chat(model="qwen2.5-coder:7b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        node.code = extract_new_implementation_from_response(res['message']['content'])

    def visit_internal(self, node: 'RequirementInternalNode'):

        # 先递归构建子节点的代码
        for child in node.children:
            if child.code == "":
                child.accept(self)

        prompt="""
        You are a top-notch Python programmer. 
        Now you have to write a python class to satisfy the following requirement: {requirement}.
        What you can do is to call the interfaces provided by the following submodules.
        {sub_module_codes}
        If the interface you need was not providede by the submodule, please let me know what kind of interface you actually need.        
        Incorporate best practices and add comments where necessary. 
        """.format(requirement=node.description, sub_module_codes=extract_submodule_codes(node))
        # If the submodules satisfy your need, present only the refactored code. Otherwise, reply 'No, I need ...' and your requirement.
        res = ollama.chat(model="qwen2.5-coder:7b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
        satisfiable = extract_satisfiability_from_response(res['message']['content'])
        if not satisfiable: # 需要修改子节点
            req = extract_child_requirement_from_response(res['message']['content'])
            node.require_child_add_interface(req)
            # 子节点修改完成，重新走一遍流程
            node.accept(self)
        else:
            # 子节点不需要修改
            node.code = extract_new_implementation_from_response(res['message']['content'])


class ConvertToDictVisitor(RequirementTreeVisitorBase):
    """
    把一棵需求树转成dict格式
    """
    def visit_leaf(self, node: 'RequirementLeafNode'):
        return {
            'en_name': node.en_name,
            'ch_name': node.ch_name,
            'description': node.description
        }
    
    def visit_internal(self, node):
        children = []
        for child in node.children:
            children.append(child.accept(self))
        return {
            'en_name': node.en_name,
            'ch_name': node.ch_name,
            'description': node.description,
            'children': children
        }



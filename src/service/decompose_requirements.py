import ollama
import re
from prompt import role, task, one_shot

# 将用户输入的需求分类为create, modify, add, delete
def requirements_classification(s:str) -> str:
    # create, modify, add, delete
    prompt = f"Classify the following requirement into one of the categories: create, modify, add, delete. Only one word is returned. \nRequirement: {s}"
    res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
    classification = res['message']['content'].lower()
    print(classification)
    if "create" in classification:
        return "create"
    elif "modify" in classification:
        return "modify"
    elif "add" in classification:
        return "add"
    elif "delete" in classification:
        return "delete"
    else:
        raise ValueError("Unable to classify the requirement.")

def decompose_requirements(requirements):
    """
    Decompose the requirements into a list of requirements.
    """

    input = """
    {
    "a": 1,
    "softwareName": "计算器",
    "moduleName": "基本运算模块"
    }
    """
    res = ollama.chat(model="llama3:8b", stream=False, messages=[{"role": "user", "content": role + task + input + one_shot}], options={"temperature": 0})

    # 提取 message 的 content
    if 'message' in res and 'content' in res['message']:
        content = res['message']['content']
        pattern = r'\[([^\]]*)\]'

        matches = re.findall(pattern, content)
        
        s="["
        # 打印匹配结果
        for match in matches:
            s+=match
        s+="]"
        print(s)
    else:
        print("message or content not found in response")

def user_confirm():
    """
    Confirm the requirements.
    """
    response = input("你确认执行吗[y]/n: ").strip().lower()
    return response == 'y' or response == ''
import ollama
import re
from prompt import role, task, one_shot

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
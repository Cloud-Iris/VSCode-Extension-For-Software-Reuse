import yaml
import os

# 传入的参数是要读取的属性名
def read_config(attribute:str):
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(project_root, 'config.yaml')

    # 读取 config.yaml 文件
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    # 获取 language 属性
    language = config.get(attribute, None)
    return language

# 示例调用
language = read_config("language")
print(f"Language: {language}")
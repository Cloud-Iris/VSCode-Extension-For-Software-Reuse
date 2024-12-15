import json

def delete_description(json_data):
    """
    删除 JSON 对象中所有对象的 description 属性
    :param json_data: 输入的 JSON 对象
    :return: 删除 description 属性后的 JSON 对象
    """
    if isinstance(json_data, dict):
        if 'description' in json_data:
            del json_data['description']
        for key, value in json_data.items():
            json_data[key] = delete_description(value)
    elif isinstance(json_data, list):
        for i in range(len(json_data)):
            json_data[i] = delete_description(json_data[i])
    return json_data



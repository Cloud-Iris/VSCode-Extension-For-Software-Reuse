import time, os
from watchdog.events import FileSystemEventHandler
import json
from requirement_tree.requirement_tree import RequirementTree
from requirement_tree.requirement_tree_node import RequirementInternalNode

class FileChangeHandler(FileSystemEventHandler):
    """
    文件修改事件处理器，用于监听文件修改事件并更新对应节点的代码。
    """
    def __init__(self, node_map, tree):
        """
        初始化 FileChangeHandler 实例。
        @param node_map: 文件名到节点的映射
        @param tree: 树结构，用于删除节点
        """
        self.node_map = node_map
        self.tree = tree
        self.last_modified = {}

    def on_modified(self, event):
        """
        当文件被修改时调用。
        @param event: 文件系统事件
        """
        if event.is_directory:
            return

        file_path = event.src_path

        # 打印事件类型以进行调试
        print(f"Event type: {event.event_type}, File: {file_path}")

        # 去重处理，确保同一个文件在短时间内只处理一次
        current_time = time.time()
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < 1:  # 1秒内的重复事件忽略
                return

        self.last_modified[file_path] = current_time

        # 如果文件是 Python 文件且在 node_map 中，更新节点的代码
        if file_path.endswith('.py') and file_path in self.node_map:
            with open(file_path, 'r') as file:
                code = file.read()
                self.node_map[file_path].code = code
                print(f"Updated code for node: {file_path}")

    def on_deleted(self, event):
        """
        当文件被删除时调用。
        @param event: 文件系统事件
        """
        if event.is_directory:
            return

        file_path = event.src_path

        # 如果文件在 node_map 中，移除对应的节点
        if file_path in self.node_map:
            node = self.node_map[file_path]
            del self.node_map[file_path]
            print(f"Removed node for deleted file: {file_path}")
            # 从树结构中删除对应的节点
            self.tree.current_node = node
            self.tree.remove_node()

def create_directory_and_files(root_en_name, file_node_map, node, path, imports):
    """
    递归创建文件夹和文件
    @param node: 当前节点
    @param path: 当前路径
    @param imports: 导入语句列表
    @param file_node_map: 文件路径到节点的映射
    """
    # 创建当前节点的文件夹
    current_path = os.path.join(path, node.en_name.replace(" ", "_"))
    os.makedirs(current_path, exist_ok=True)

    # 如果是叶子节点，创建文件
    if len(node.children) == 0:
        file_path = os.path.join(current_path, f"{node.en_name.replace(' ', '_')}.py")
        with open(file_path, 'w') as file:
            file.write(node.code)
        node.file_path = file_path
        file_node_map[file_path] = node
        return

    # 递归处理子节点
    for child in node.children:
        create_directory_and_files(root_en_name, file_node_map, child, current_path, imports)
        print("child.file_path", child.file_path)
        # 添加导入语句
        module_path = child.file_path[child.file_path.index(root_en_name)+len(root_en_name)+1:child.file_path.rindex('.')]
        # 使用 os.path 的路径分隔符在 Windows 上是反斜杠 (\)，在 Unix 上是斜杠 (/)
        module_path = module_path.replace(os.sep, '.')  # 将路径分隔符替换为点号
        imports.append(f"from {module_path} import *")

    # 回溯时创建当前节点的文件
    file_path = os.path.join(current_path, f"{node.en_name.replace(' ', '_')}.py")
    with open(file_path, 'w') as file:
        # 写入导入语句
        file.write("\n".join(imports) + "\n\n")
        file.write(node.code)
    node.file_path = file_path
    file_node_map[file_path] = node

# 将树结构存入根目录的.json文件中
def save_tree_to_json(tree, path):
    """
    将树结构存入.json文件中
    @param tree: 树结构
    @param path: 存储路径
    """
    def node_to_dict(node):
        return {
            "en_name": node.en_name,
            "ch_name": node.ch_name,
            "description": node.description,
            "file_path": node.file_path,
            "parent": str(node.parent.id) if node.parent else "",
            "code": node.code,
            "id": str(node.id),
            "children": [node_to_dict(child) for child in node.children]
        }

    with open(path, 'w', encoding="utf-8") as file:
        json.dump(node_to_dict(tree.root), file, ensure_ascii=False, indent=4)

# 从.json文件中加载树结构
def load_tree_from_json(path):
    """
    从.json文件中加载树结构
    @param path: .json文件路径
    @return: 加载的树结构
    """
    def dict_to_node(node_dict):
        node = RequirementInternalNode(node_dict["en_name"], node_dict["ch_name"], node_dict["description"], node_dict["file_path"])
        # node.id = uuid.UUID(node_dict["id"])
        node.code = node_dict["code"]
        for child_dict in node_dict["children"]:
            child_node = dict_to_node(child_dict)
            node.children.append(child_node)
            child_node.parent = node
        return node

    with open(path, 'r', encoding="utf-8") as file:
        tree_dict = json.load(file)
        tree = RequirementTree(tree_dict["en_name"], tree_dict["ch_name"], tree_dict["description"], tree_dict["file_path"])
        tree.root = dict_to_node(tree_dict)
        return tree
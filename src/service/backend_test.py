from decompose_requirements import RequirementManager
import os

if __name__ == "__main__":
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 确保 workspace 文件夹存在
    workspace_dir = os.path.join(project_root, "workspace")
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)

    # 将项目根目录的 workspace 文件夹路径传递给 RequirementManager
    manager = RequirementManager(workspace_dir)
    manager.user_interaction()
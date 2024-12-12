from decompose_requirements import RequirementManager
import sys, os
import ollama
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), './config'))
from get_config import read_config

if __name__ == "__main__":
    # 获取当前时间并格式化为字符串
    current_time = datetime.now().strftime("%Y%m%d_%H")

    # 使用当前时间作为日志文件名
    log_filename = os.path.join(os.path.dirname(__file__), "log/{}.log".format(current_time))

    with open(log_filename, "w") as f:
        f.write("")  # 创建一个空文件

    # Redirect print output to log file
    class Logger(object):
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, "a")

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            pass

    sys.stdout = Logger(log_filename)

    # print(RequirementManager.agent_imitate_user())

    manager = RequirementManager(os.path.join(os.path.dirname(__file__), 'workspace'))
    manager.agent_interaction()
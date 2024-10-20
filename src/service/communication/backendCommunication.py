from flask import Flask, request, jsonify
from decompose_requirements import RequirementManager
import os

class BackendService:
    def __init__(self):
        self.app = Flask(__name__)
        self.parsed_str = ""
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/receive-folder-path', methods=['POST'])
        def receive_folder_path():
            data = request.get_json()
            self.parsed_str = data.get('folderPath', '')
            print("项目根目录是: "+self.parsed_str)
            return jsonify({'parsedStr': self.parsed_str})

        @self.app.route('/health-check', methods=['GET'])
        def health_check():
            return jsonify({'status': 'ok'})

        @self.app.after_request
        def after_request(response):
            """
            在请求处理后执行的操作
            """
            # 这里可以执行一些请求后的操作
            manager = RequirementManager(self.parsed_str)
            manager.user_interaction()
            os._exit(0)
            return response

    def run(self, port=5000):
        self.app.run(port=port)
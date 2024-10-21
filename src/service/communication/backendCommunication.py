from flask import Flask, request, jsonify
# 解决跨域问题 pip install Flask-Cors
from flask_cors import CORS
from decompose_requirements import RequirementManager
import os
from file_system.fileChange import load_tree_from_json

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
        
        @self.app.route('/depose-req-for-level-2', methods=['GET', 'POST'])
        def depose_req_for_level_2():
            data:dict = request.get_json()
            req:str = data.get('req', '')
            # TODO: 这个是前端传过来的用户原始需求描述
            # print(req)

            _2LevelReqs = [
                f"默认 2 级需求 111 for {req}",
                f"默认 2 级需求 222 for {req}",
                f"默认 2 级需求 333 for {req}"
            ]
            return jsonify({'_2LevelReqs': _2LevelReqs})

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
        CORS(self.app)  # 解决跨域问题
        self.app.run(port=port)
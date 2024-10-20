import * as vscode from 'vscode';
import axios from 'axios';
import { spawn } from 'child_process';

let hasExecuted = false;

export async function sendFolderPathToBackend() {
    if (hasExecuted) {
        return;
    }
    hasExecuted = true;

    // 打开命令行并运行指定的 Python 脚本
    const pythonProcess = spawn('cmd', ['/c', 'start', 'cmd', '/k', 'D:/usualsoft/anaconda/envs/reuse-tree/python.exe', 'D:\\learn\\pku_work\\lowcode\\20241017-demo\\VSCode-Extension-For-Software-Reuse\\src\\service\\main.py']);

    pythonProcess.on('error', (error) => {
        console.error(`Error executing Python script: ${error.message}`);
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python script stdout: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python script stderr: ${data}`);
    });

    // 获取当前工作区的文件夹路径
    const workspaceFolders = vscode.workspace.workspaceFolders;
    let currentFolderPath = '';
    if (workspaceFolders && workspaceFolders.length > 0) {
        currentFolderPath = workspaceFolders[0].uri.fsPath;
        console.log(`Current folder path: ${currentFolderPath}`);
    }

    // 轮询等待后端服务器启动
    const maxRetries = 10;
    const retryInterval = 2000; // 2 seconds

    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await axios.post('http://localhost:5000/receive-folder-path', {
                folderPath: currentFolderPath
            });
            console.log('Response from backend:', response.data);
            return; // 成功后退出函数
        } catch (error) {
            // console.error('Error sending folder path to backend, retrying...', error);
            await new Promise(resolve => setTimeout(resolve, retryInterval));
        }
    }

    console.error('Failed to connect to backend after multiple attempts.');
}
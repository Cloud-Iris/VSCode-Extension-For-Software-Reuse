import * as vscode from 'vscode';
import axios from 'axios';

let hasExecuted = false;

export async function sendFolderPathToBackend() {
    if (hasExecuted) {
        return;
    }
    hasExecuted = true;

    // 创建一个新的 VSCode 集成终端并运行指定的 Python 脚本
    const terminal = vscode.window.createTerminal('Python Script');
    const pythonPath = 'D:/usualsoft/anaconda/envs/reuse-tree/python.exe';
    const scriptPath = 'D:/learn/pku_work/lowcode/20241017-demo/VSCode-Extension-For-Software-Reuse/src/service/main.py';
    terminal.sendText(`${pythonPath} ${scriptPath}`);
    terminal.show();

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

    // 睡眠0.1秒
    await new Promise(resolve => setTimeout(resolve, 100));

    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await axios.post('http://localhost:5000/receive-folder-path', {
                folderPath: currentFolderPath
            });
            console.log('Response from backend:', response.data);
            return; // 成功后退出函数
        } catch (error) {
            console.error('Error sending folder path to backend, retrying...', error);
            await new Promise(resolve => setTimeout(resolve, retryInterval));
        }
    }

    console.error('Failed to connect to backend after multiple attempts.');
}
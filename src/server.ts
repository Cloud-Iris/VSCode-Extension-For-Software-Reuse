import * as vscode from 'vscode';
import * as path from 'path';
import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: 'http://localhost:5000',
    timeout: 1000,
});

// 服务器是否正在运行
let isServerRunning = false;


/**
 * 启动 Flask 服务器，并返回服务器运行状态
 * @param context 
 * @returns 
 */
export async function startFlaskServer(context: vscode.ExtensionContext) {
    if (isServerRunning) {
        vscode.window.showInformationMessage('Flask server is already running.');
        return true;
    }
    isServerRunning = true;

    // 创建一个新的 VSCode 集成终端并运行指定的 Python 脚本，启动 Flask 服务器
    const terminal = vscode.window.createTerminal('Flask Server');

    // 尝试从 VS Code 设置中获取 Python 解释器路径
    let pythonPath: string | undefined;
    pythonPath = vscode.workspace.getConfiguration('python').get<string>('pythonPath');
    if (!pythonPath) {
        // 尝试从环境变量中获取 Python 解释器路径，只用 python 默认用户设置了环境变量
        pythonPath = process.env.PYTHON_PATH || process.env.PYTHON || 'python';
    }
    if (!pythonPath) {
        vscode.window.showErrorMessage('Could not find Python interpreter. 请确认python解释器已安装并配置环境变量');
        return;
    }
    vscode.window.showInformationMessage('Python interpreter path: ' + pythonPath);

    const scriptPath = path.join(context.extensionPath, 'src/service/main.py');
    terminal.sendText(`${pythonPath} ${scriptPath}`);
    terminal.show();

    return await sendFolderPathToBackend();
}


/**
 * 通过轮询等待后端服务器启动，发送插件工作区的文件夹路径
 * @returns Promise<boolean> 是否成功发送文件夹路径
 */
const sendFolderPathToBackend = async () => {
    // 获取当前工作区的文件夹路径
    const workspaceFolders = vscode.workspace.workspaceFolders;
    let currentFolderPath = '';
    if (workspaceFolders && workspaceFolders.length > 0) {
        currentFolderPath = workspaceFolders[0].uri.fsPath;
        vscode.window.showInformationMessage(`Current folder path: ${currentFolderPath}`);
    }

    // 轮询等待后端服务器启动
    const maxRetries = 10;
    const retryInterval = 2000; // 1 seconds

    // 睡眠2秒
    await new Promise(resolve => setTimeout(resolve, 2000));

    for (let i = 0; i < maxRetries; i++) {
        try {
            // 后端服务器已启动，发送文件路径
            const response = await axiosInstance.post('/receive-folder-path', {
                folderPath: currentFolderPath
            });
            console.log('后端成功收到了当前工作区路径', response.data);
            // 成功后立即退出函数
            return true;
        } catch (error) {
            console.error('向后端发送文件夹路径时出错', error);
            // 失败后等待一段时间后重试
            await new Promise(resolve => setTimeout(resolve, retryInterval));
        }
    }
    // 所有重试均失败，打印错误信息
    console.error('Failed to connect to backend after multiple attempts.');
    return false;
};


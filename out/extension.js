"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
function activate(context) {
    console.log('Congratulations, your extension "software-reuse-extension" is now active!');
    // 注册一个命令，触发显示侧边栏
    const disposable = vscode.commands.registerCommand('software-reuse-extension.showSidebar', () => {
        vscode.window.showInformationMessage('插件成功打开侧边栏!');
        const panel = vscode.window.createWebviewPanel('sidebar', // 视图类型
        'My Sidebar', // 显示标题
        vscode.ViewColumn.Two, // 显示在侧边栏
        {
            enableScripts: true, // 允许脚本
            retainContextWhenHidden: true // 在隐藏时保留状态
        });
        // 读取 HTML 和 JavaScript 文件内容并赋值给 Webview
        const htmlFilePath = path.join(context.extensionPath, 'src/sidebar-webview.html');
        const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
        panel.webview.html = htmlContent;
        // 处理来自 Webview 的消息
        panel.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'showAlert':
                    showHtmlInWebview(context, message.text);
                    // vscode.window.showInformationMessage('You clicked on: ' + message.text, 'Confirm', 'Cancel')
                    //     .then(selection => {
                    //         if (selection === 'Confirm') {
                    //             vscode.window.showInformationMessage('You confirmed: ' + message.text);
                    //         }
                    //     });
                    break;
                case 'openEditorDialog':
                    vscode.window.showInformationMessage('插件成功打开编辑器对话框!');
                    break;
            }
        }, undefined, context.subscriptions);
    });
    context.subscriptions.push(disposable);
}
function showHtmlInWebview(context, text) {
    const panel = vscode.window.createWebviewPanel('htmlDisplay', // 视图类型
    'HTML Display', // 显示标题
    vscode.ViewColumn.One, // 显示在编辑器中间
    {
        enableScripts: true // 允许脚本
    });
    const htmlFilePath = path.join(context.extensionPath, 'src/content.html');
    const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
    panel.webview.html = htmlContent.replace('{{text}}', text);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map
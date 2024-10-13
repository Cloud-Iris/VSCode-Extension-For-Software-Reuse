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
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = __importStar(require("vscode"));
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
function activate(context) {
    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('Congratulations, your extension "software-reuse-extension" is now active!');
    // The command has been defined in the package.json file
    // Now provide the implementation of the command with registerCommand
    // The commandId parameter must match the command field in package.json
    // 注册一个命令，触发显示侧边栏
    const disposable = vscode.commands.registerCommand('software-reuse-extension.showSidebar', () => {
        // The code you place here will be executed every time your command is executed
        // Display a message box to the user
        vscode.window.showInformationMessage('插件成功启动!');
        const panel = vscode.window.createWebviewPanel('sidebar', // 视图类型
        'My Sidebar', // 显示标题
        vscode.ViewColumn.Two, // 显示在侧边栏
        {
            enableScripts: true, // 允许脚本
            retainContextWhenHidden: true // 在隐藏时保留状态
        });
        // Webview 内容，HTML 和 JavaScript
        panel.webview.html = getWebviewContent();
        // 处理来自 Webview 的消息
        panel.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'showAlert':
                    vscode.window.showInformationMessage('You clicked on: ' + message.text, 'Confirm', 'Cancel')
                        .then(selection => {
                        if (selection === 'Confirm') {
                            vscode.window.showInformationMessage('You confirmed: ' + message.text);
                        }
                    });
                    break;
            }
        }, undefined, context.subscriptions);
    });
    context.subscriptions.push(disposable);
}
// This method is called when your extension is deactivated
function deactivate() { }
function getWebviewContent() {
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <h1>Uneditable Document</h1>
        <p>This is a static document. Click on the <a href="#" id="clickable-text">clickable text</a>.</p>
        
        <script>
            const vscode = acquireVsCodeApi();

            document.getElementById('clickable-text').addEventListener('click', () => {
                vscode.postMessage({
                    command: 'showAlert',
                    text: 'the clickable text'
                });
            });
        </script>
    </body>
    </html>`;
}
//# sourceMappingURL=extension.js.map
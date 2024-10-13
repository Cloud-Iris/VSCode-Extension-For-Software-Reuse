import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export function activate(context: vscode.ExtensionContext) {

	console.log('Congratulations, your extension "software-reuse-extension" is now active!');

	// 注册一个命令，触发显示侧边栏
	const disposable = vscode.commands.registerCommand('software-reuse-extension.showSidebar', () => {
		vscode.window.showInformationMessage('插件成功打开侧边栏!');

		const panel = vscode.window.createWebviewPanel(
            'sidebar', // 视图类型
            'My Sidebar', // 显示标题
            vscode.ViewColumn.Two, // 显示在侧边栏
            {
                enableScripts: true, // 允许脚本
                retainContextWhenHidden: true // 在隐藏时保留状态
            }
        );

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
                    showWindowQuickPick();
                    break;
            }
        }, undefined, context.subscriptions);
	});

	context.subscriptions.push(disposable);
}

function showHtmlInWebview(context: vscode.ExtensionContext, text: string) {
    const panel = vscode.window.createWebviewPanel(
        'htmlDisplay', // 视图类型
        'HTML Display', // 显示标题
        vscode.ViewColumn.One, // 显示在编辑器中间
        {
            enableScripts: true // 允许脚本
        }
    );

    const htmlFilePath = path.join(context.extensionPath, 'src/content.html');
    const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');

    panel.webview.html = htmlContent.replace('{{text}}', text);
}

export function deactivate() {}

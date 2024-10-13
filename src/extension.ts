import * as vscode from 'vscode';

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

export function deactivate() {}


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

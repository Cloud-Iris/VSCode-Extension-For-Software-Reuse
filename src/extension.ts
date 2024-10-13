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
                    vscode.window.showInformationMessage('You clicked on: ' + message.text, 'Confirm', 'Cancel')
                        .then(selection => {
                            if (selection === 'Confirm') {
                                vscode.window.showInformationMessage('You confirmed: ' + message.text);
                            }
                        });
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

async function showWindowQuickPick() {
    // 选项卡和默认内容
    const tabOptions: { [key: string]: string } = {
        'Option 1': 'Default content for Option 1',
        'Option 2': 'Default content for Option 2',
        'Option 3': 'Default content for Option 3'
    };

    // 使用 quick pick 让用户选择一个选项
    const selectedOption = await vscode.window.showQuickPick(Object.keys(tabOptions), {
        placeHolder: '选择一个选项卡进行编辑',
        canPickMany: false
    });

    if (selectedOption) {
        // 显示一个输入框让用户编辑内容
        const userInput = await vscode.window.showInputBox({
            prompt: `Edit content for ${selectedOption}`,
            placeHolder: 'Type your content here',
            value: tabOptions[selectedOption] // 设置默认内容
        });

        if (userInput) {
            // 将编辑的内容插入到当前活动的编辑器中
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const position = editor.selection.active;
                editor.edit(editBuilder => {
                    editBuilder.insert(position, userInput);
                });
                vscode.window.showInformationMessage(`${selectedOption} content added to the editor.`);
            } else {
                vscode.window.showErrorMessage('No active editor found.');
            }
        }
    }
}

export function deactivate() {}

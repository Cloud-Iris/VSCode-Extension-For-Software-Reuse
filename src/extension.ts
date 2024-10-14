import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

let activeEditor: vscode.TextEditor | undefined;
let cursorPosition: vscode.Position | undefined;

// 保存当前编辑器状态
const saveEditorState = () => {
    activeEditor = vscode.window.activeTextEditor;
    if (activeEditor) {
        cursorPosition = activeEditor.selection.active;
        // console.log(activeEditor, cursorPosition);
    }
};

// 恢复编辑器焦点并插入文本
const restoreEditorStateAndInsertText = async (text: string) => {
    if (activeEditor && cursorPosition) {
        // 重新打开编辑器并聚焦
        try {
            await vscode.window.showTextDocument(activeEditor.document, vscode.ViewColumn.One);
            // 在保存的光标位置插入文本
            console.log(`即将插入 code 的位置是 Line:${cursorPosition.line}, Character:${cursorPosition.character}`);
            const success = await activeEditor.edit(editBuilder => {
                editBuilder.insert(cursorPosition!, text);
            });
            if (success) {
                vscode.window.showInformationMessage('Content added to the editor.');
            } else {
                vscode.window.showErrorMessage('Failed to edit the document.');
            }

        } catch (error) {
            vscode.window.showErrorMessage('Error restoring editor state: ' + error);
        }
    } else {
        vscode.window.showErrorMessage('No active editor found or lost focus.');
    }
};

// async function showWindowQuickPick() {
//     // 选项卡和默认内容
//     const tabOptions: { [key: string]: string } = {
//         'Option 1': 'Default content for Option 1',
//         'Option 2': 'Default content for Option 2',
//         'Option 3': 'Default content for Option 3'
//     };

//     // 使用 quick pick 让用户选择一个选项
//     const selectedOption = await vscode.window.showQuickPick(Object.keys(tabOptions), {
//         placeHolder: '选择一个选项卡进行编辑',
//         canPickMany: false
//     });

//     if (selectedOption) {
//         // 显示一个输入框让用户编辑内容
//         const userInput = await vscode.window.showInputBox({
//             prompt: `Edit content for ${selectedOption}`,
//             // placeHolder: 'Type your content here',
//             value: tabOptions[selectedOption] // 设置默认内容
//         });

//         if (userInput) {
//             restoreEditorStateAndInsertText(userInput);
//         }
//     }
// }

// 监听编辑器的焦点变化，实时更新光标位置
vscode.window.onDidChangeTextEditorSelection(event => {
    if (event.textEditor === vscode.window.activeTextEditor) {
        activeEditor = event.textEditor;
        cursorPosition = event.selections[0].active;
        console.log(activeEditor);
        console.log(cursorPosition);
    } else {
        console.log(event.textEditor);
    }
});

export function activate(context: vscode.ExtensionContext) {

	console.log('Congratulations, your extension "software-reuse-extension" is now active!');

    saveEditorState(); // 在显示 showSidebar Webview 前保存编辑器状态

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
                    vscode.window.showInformationMessage('插件成功打开编辑器对话框!·');
                    // showWindowQuickPick();
                    const panel = vscode.window.createWebviewPanel(
                        'htmlDisplay', // 视图类型
                        'HTML Display', // 显示标题
                        vscode.ViewColumn.Beside, // 显示在编辑器旁边
                        {
                            enableScripts: true // 允许脚本
                        }
                    );
                
                    const htmlFilePath = path.join(context.extensionPath, 'src/content-webview.html');
                    const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
                    panel.webview.html = htmlContent;

                    panel.webview.onDidReceiveMessage(async message => {
                        switch (message.command) {
                            case 'acceptCode':
                                vscode.window.showInformationMessage('接受 code!' + message.text);
                                panel.dispose();  // 关闭 Webview
                                await restoreEditorStateAndInsertText(message.text);
                                break;
            
                            case 'rejectCode':
                                vscode.window.showInformationMessage('拒绝 code!');
                                panel.dispose();  // 关闭 Webview
                                break;
                        }
                    });
                    break;

            }
        }, undefined, context.subscriptions);
	});

	context.subscriptions.push(disposable);
}

export function deactivate() {}

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

// 监听编辑器的焦点变化，实时更新光标位置
vscode.window.onDidChangeTextEditorSelection(event => {
    if (event.textEditor === vscode.window.activeTextEditor) {
        activeEditor = event.textEditor;
        cursorPosition = event.selections[0].active;
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
            '需求大纲 Requirement Outline', // 显示标题
            vscode.ViewColumn.Two, // 显示在侧边栏
            {
                enableScripts: true, // 允许脚本
                retainContextWhenHidden: true // 在隐藏时保留状态
            }
        );

        // 打开插件的 “需求大纲” 侧边栏
        const htmlFilePath = path.join(context.extensionPath, 'src/webviews/sidebar-requirement.html');
		// 读取 HTML 和 JavaScript 文件内容并赋值给 Webview
        const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
        panel.webview.html = htmlContent;

        // 记录当前打开的 code suggestion panel
        let activeInnerPanel: vscode.WebviewPanel | undefined;

        // 处理来自 Webview 的消息
		panel.webview.onDidReceiveMessage(async message => {
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

                    if (activeInnerPanel) {
                        activeInnerPanel.dispose();
                    }

                    const codeSuggestionPanel = vscode.window.createWebviewPanel(
                        'htmlDisplay', // 视图类型
                        '代码建议 Code Suggestion', // 显示标题
                        vscode.ViewColumn.Three, // 显示在编辑器旁边
                        {
                            enableScripts: true // 允许脚本
                        }
                    );

                    activeInnerPanel = codeSuggestionPanel;
                    
                    // 打开插件的 “代码建议” 侧边栏
                    const htmlFilePath = path.join(context.extensionPath, 'src/webviews/sidebar-code.html');
                    const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
                    codeSuggestionPanel.webview.html = htmlContent;

                    codeSuggestionPanel.webview.onDidReceiveMessage(async message => {
                        switch (message.command) {
                            case 'acceptCode':
                                vscode.window.showInformationMessage('接受 code!' + message.text);
                                codeSuggestionPanel.dispose();  // 关闭 Webview
                                await restoreEditorStateAndInsertText(message.text);
                                break;
            
                            case 'rejectCode':
                                vscode.window.showInformationMessage('拒绝 code!');
                                codeSuggestionPanel.dispose();  // 关闭 Webview
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

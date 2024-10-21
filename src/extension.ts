import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { sendFolderPathToBackend } from './service/communication/frontCommunication';

export function activate(context: vscode.ExtensionContext) {
    console.log('Congratulations, your extension "software-reuse-extension" is now active!');

    // 在显示 showSidebar Webview 前保存编辑器状态
    saveEditorState();

    sendFolderPathToBackend();

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('myWebviewView', new MyWebviewViewProvider(context))
    );

    console.log('WebviewViewProvider 注册完毕');
}

export function deactivate() {}


class MyWebviewViewProvider implements vscode.WebviewViewProvider {

    private _view?: vscode.WebviewView;

    constructor(private readonly _context: vscode.ExtensionContext) {}

    // 提供给 viewsContainer 的 view 的 type 为 webwebview
    resolveWebviewView(webviewView: vscode.WebviewView) {
        console.log("resolveWebviewView 函数被调用");

        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true
        };

        // 设置 Webview 的 HTML 内容
        const htmlFilePath = path.join(this._context.extensionPath, 'src/webviews/sidebar-requirement.html');
        const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
        // 设置 Webview 的 CSS 路径【将本地文件的相对路径转换为 Webview 可以访问的 VScode URI】
        const cssFilePath = webviewView.webview.asWebviewUri(
            vscode.Uri.joinPath(this._context.extensionUri, 'src', 'webviews', 'css', 'style-requirement.css')
        );
        webviewView.webview.html = htmlContent.replace('###CSS', cssFilePath.toString());

        // 记录当前打开的 code suggestion panel
        let activeInnerPanel: vscode.WebviewPanel | undefined;

        // 处理 Webview 发来的消息
        webviewView.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'openEditorDialog':
                    vscode.window.showInformationMessage('插件成功打开编辑器对话框!');
                    
                    if (activeInnerPanel) {
                        activeInnerPanel.dispose();
                    }
                    const codeSuggestionPanel = vscode.window.createWebviewPanel(
                        'htmlDisplay', // 视图类型
                        '代码建议 Code Suggestion', // 显示标题
                        vscode.ViewColumn.Beside, // 显示在编辑器旁边
                        {
                            enableScripts: true // 允许脚本
                        }
                    );
                    activeInnerPanel = codeSuggestionPanel;

                    // 打开插件的 “代码建议” 侧边栏
                    const htmlFilePath = path.join(this._context.extensionPath, 'src/webviews/sidebar-code.html');
                    const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
                    codeSuggestionPanel.webview.html = htmlContent;

                    codeSuggestionPanel.webview.onDidReceiveMessage(async message => {
                        switch (message.command) {
                            case 'acceptCode':
                                vscode.window.showInformationMessage('接受 code!' + message.text);
                                codeSuggestionPanel.dispose();  // 关闭 Webview
                                // 如果记录下了 编辑器状态 和 光标位置
                                if (activeEditor && cursorPosition) {
                                    await restoreEditorStateAndInsertText(message.text, activeEditor, cursorPosition);
                                } else {
                                    // 用户第一次进入工作区但是没有打开任何文件时，新建一个文件
                                    let newDate = new Date().toISOString();
                                    await createFileAndInsertText(`${
                                        newDate.substring(0, 10)
                                    }`, message.text);
                                }
                                break;
            
                            case 'rejectCode':
                                vscode.window.showInformationMessage('拒绝 code!');
                                codeSuggestionPanel.dispose();  // 关闭 Webview
                                break;
                        }
                    });
                    break;
            }
        });
    }

    // 在需要时更新 Webview 的内容
    updateWebviewContent(html: string) {
        if (this._view) {
            this._view.webview.html = html;
        }
    }
}


let activeEditor: vscode.TextEditor | undefined;
let cursorPosition: vscode.Position | undefined;

// 保存当前编辑器状态
const saveEditorState = () => {
    activeEditor = vscode.window.activeTextEditor;
    if (activeEditor) {
        cursorPosition = activeEditor.selection.active;
        console.log(activeEditor.document.fileName, cursorPosition);
    }
};

/**
 * 重新打开编辑器，恢复编辑器焦点，并插入文本
 * @param text 要插入的文本
 * @param activeEditor 存储的编辑器状态
 * @param cursorPosition 存储的光标位置
 */
const restoreEditorStateAndInsertText = async (
    text: string, 
    activeEditor: vscode.TextEditor, 
    cursorPosition: vscode.Position
) => {
    const document = activeEditor.document;
    // 检查当前编辑器是否仍然可见
    const isVisible = vscode.window.visibleTextEditors.some(editor => editor.document === document);
    
    if (!activeEditor || !isVisible) {
        // 有的文件可能已经被 手动关闭 或者 删除了
        vscode.window.showWarningMessage('请重新打开对应的文件 The active editor is closed. Please open the document again.');
        vscode.window.showWarningMessage('系统会先为您生成一个空白文件并插入您的选择');
        await createFileAndInsertText(`${new Date().toISOString().substring(0, 10)}`, text);
        console.log(vscode.window.activeTextEditor);
        console.log(activeEditor);
        return;  // 直接返回，避免后续操作
    }
    // 重新打开编辑器并聚焦
    try {
        await vscode.window.showTextDocument(activeEditor.document, vscode.ViewColumn.One);
        // 在保存的光标位置插入文本
        console.log(`即将插入 code 的文件是 file:${activeEditor.document.fileName} Line:${cursorPosition.line}, Character:${cursorPosition.character}`);
        const success = await activeEditor.edit(editBuilder => {
            editBuilder.insert(cursorPosition!, text);
        });
        success
        ? vscode.window.showInformationMessage('Content added to the editor.')
        : vscode.window.showErrorMessage('Failed to edit the document.');
    } catch (error) {
        vscode.window.showErrorMessage('Error restoring editor state: ' + error);
        // vscode.window.showInformationMessage('尝试创建文件填入内容');
        // await createFileAndInsertText(activeEditor.document.fileName, text);
    }
};

// 监听编辑器的焦点变化，实时更新光标位置
vscode.window.onDidChangeTextEditorSelection(event => {
    if (event.textEditor === vscode.window.activeTextEditor) {
        activeEditor = event.textEditor;
        cursorPosition = event.selections[0].active;
        console.log(activeEditor.document.fileName, cursorPosition);
    } else {
        console.log(event.textEditor);
    }
});

/**
 * 由于 activeEditor 为空，说明用户在打开插件sidebar的时候 “打开了工作区但是没有打开任何一个文件”，或者“没有打开工作区”。
 * 1. 用户已打开工作区但没有打开任何文件时，创建一个新文件，将 text 插入其中。
 * 2. 用户没有打开工作区时，弹出警告提示。
 * @param fileName 文件名
 * @param text 要插入的文本
 */
const createFileAndInsertText = async (fileName: string, text: string) => {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
        // 用户已打开工作区但没有打开任何文件
        const rootPath = workspaceFolders[0].uri.fsPath;
        const filePath = path.join(rootPath, fileName);
        try {
            // 将一个本地文件系统路径转换为一个 Uri 对象。与 VSCode 文件系统（包括远程文件系统或虚拟工作区）无缝对接
            const fileUri = vscode.Uri.file(filePath);

            // 创建目录，如果不存在的话
            const directoryUri = vscode.Uri.file(path.dirname(filePath));
            await vscode.workspace.fs.createDirectory(directoryUri);

            // 写入文件
            await vscode.workspace.fs.writeFile(fileUri, Buffer.from(text, 'utf8'));
            // 打开新文件并插入文本
            const document = await vscode.workspace.openTextDocument(fileUri);
            await vscode.window.showTextDocument(document);

            vscode.window.showInformationMessage(`File ${fileName} created and text inserted.`);
        } catch (error) {
            vscode.window.showErrorMessage('Error creating file: ' + error);
        }
    } else {
        // 没有打开工作区
        vscode.window.showErrorMessage('No workspace folder found. 请先打开一个工作区再使用插件');
    }
};
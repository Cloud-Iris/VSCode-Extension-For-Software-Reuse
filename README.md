# software-reuse-extension README

VS Code 插件的开发需要安装 Yeoman 和 VS Code Extension generator。我这里是全局安装了，所以没有加入依赖：`npm install --global yo generator-code`。

> 如果需要自己创造一个新的插件目录，请执行 `yo code`。在本项目中不需要这么做。

请执行 `npm install` 安装依赖后再进行开发。

进入 `src/extension.ts`，可以选择按下 F5 或者执行 `Debug: Start Debugging` 命令，从而打开一个 VS Code 窗口运行插件效果。

在成功运行插件后会在控制台看到 `Congratulations, your extension "software-reuse-extension" is now active!`。

## Features

目前插件功能只有 **打开侧边栏**，我配置了一个按钮可以触发 vscode 底部的消息弹出。

### 打开侧边栏

命令执行：`Open Sidebar For Software Reuse`

快捷键： `ctrl + shift + alt + o` （ MAC 是 `cmd + shift + alt + o`）

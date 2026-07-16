# 成行 OS Skills 安装指南

本仓库同时支持 Claude Code 和 Codex 的原生插件 Marketplace。兼容安装器只用于尚未提供 `codex plugin` 命令的旧环境。

## 安装前检查

在终端分别运行：

```bash
claude --version
claude plugin --help
codex --version
codex plugin --help
```

只安装实际使用的平台。若对应的 `plugin --help` 无法正常显示帮助，先更新或修复客户端。

## Claude Code

### 安装

```bash
claude plugin marketplace add githubume/chengxing-os-skills
claude plugin install habit-rebuild@chengxing-os-skills
claude plugin install parent-learning@chengxing-os-skills
claude plugin install conflict-reset@chengxing-os-skills
```

### 验证

```bash
claude plugin marketplace list
claude plugin list
```

应能看到 `chengxing-os-skills` Marketplace，以及三个状态为 enabled 的插件。随后重新启动 Claude Code。

### 升级

```bash
claude plugin marketplace update chengxing-os-skills
claude plugin update habit-rebuild@chengxing-os-skills
claude plugin update parent-learning@chengxing-os-skills
claude plugin update conflict-reset@chengxing-os-skills
```

升级后重新启动 Claude Code。

### 卸载

```bash
claude plugin uninstall habit-rebuild@chengxing-os-skills
claude plugin uninstall parent-learning@chengxing-os-skills
claude plugin uninstall conflict-reset@chengxing-os-skills
claude plugin marketplace remove chengxing-os-skills
```

## Codex

### 原生安装（推荐）

```bash
codex plugin marketplace add githubume/chengxing-os-skills
codex plugin add habit-rebuild@chengxing-os-skills
codex plugin add parent-learning@chengxing-os-skills
codex plugin add conflict-reset@chengxing-os-skills
```

### 验证

```bash
codex plugin marketplace list
codex plugin list
```

应能看到 `chengxing-os-skills` Marketplace，以及三个 installed、enabled 的插件。随后新建一个 Codex 任务，让新任务加载插件。

### 升级

```bash
codex plugin marketplace upgrade chengxing-os-skills
codex plugin add habit-rebuild@chengxing-os-skills
codex plugin add parent-learning@chengxing-os-skills
codex plugin add conflict-reset@chengxing-os-skills
```

插件发布新版本后，刷新 Marketplace 并重新执行 `plugin add`。随后新建 Codex 任务。

### 卸载

```bash
codex plugin remove habit-rebuild@chengxing-os-skills
codex plugin remove parent-learning@chengxing-os-skills
codex plugin remove conflict-reset@chengxing-os-skills
codex plugin marketplace remove chengxing-os-skills
```

## Codex 兼容安装器

只有当 `codex plugin --help` 不存在，但当前 Codex 仍能发现 `~/.codex/skills` 时，才使用此方式：

```bash
git clone --depth 1 https://github.com/githubume/chengxing-os-skills.git
python3 chengxing-os-skills/scripts/manage_codex_adapters.py install
python3 chengxing-os-skills/scripts/manage_codex_adapters.py verify
```

升级：

```bash
git -C chengxing-os-skills pull --ff-only
python3 chengxing-os-skills/scripts/manage_codex_adapters.py upgrade
python3 chengxing-os-skills/scripts/manage_codex_adapters.py verify
```

卸载：

```bash
python3 chengxing-os-skills/scripts/manage_codex_adapters.py uninstall
```

兼容安装器只管理带成行 OS 标记的 adapter 和 vendor 目录，不会删除其他 Skill，也不会删除 `~/.chengxing-os` 用户数据。

## 常见错误

### `codex` 报 `ENOENT` 或找不到平台二进制

这说明 Codex CLI 自身安装不完整，不是本仓库 Marketplace 或插件清单错误。先重新安装或更新 Codex CLI，再确认：

```bash
codex --version
codex plugin --help
```

macOS 上如果桌面应用可用、终端命令损坏，可以先用应用内置程序确认问题范围：

```bash
/Applications/ChatGPT.app/Contents/Resources/codex --version
```

该绝对路径只用于本机诊断，不应作为跨平台安装命令。

### Marketplace 克隆或升级超时

确认能够访问 GitHub 后重试原命令。超时过程中不要手工移动半成品缓存目录；客户端会在下一次成功操作时重新建立 Marketplace 快照。

### Claude Code 在自动化环境报告 `/dev/tty`

请在正常交互式终端中执行 Marketplace 添加与插件安装。README 中的命令面向人工安装，不是无交互 CI 安装脚本。

### 安装后没有触发

- Claude Code：完成安装或升级后重新启动。
- Codex：完成安装或升级后新建任务。
- 先用 `plugin list` 确认插件已安装并启用，再用自然语言描述问题，不需要记忆斜杠命令。

## 数据边界

卸载插件不会自动删除 `~/.chengxing-os`。如需处理画像或案例，应先查看并确认数据范围，再由用户主动决定是否删除。

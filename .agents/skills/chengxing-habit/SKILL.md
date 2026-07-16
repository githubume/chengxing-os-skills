---
name: chengxing-habit
description: Use when an adult wants to change a recurring low-risk personal behavior such as procrastination, bedtime phone use, delayed sleep routines, exercise avoidance, or habit relapse. This Codex compatibility adapter routes natural-language requests to the independent Chengxing OS habit-rebuild plugin and its B1/B2/B3 workflow.
license: Apache-2.0
---

<!-- chengxing-os-managed-adapter -->

# 成行 OS 习惯重建 Codex Adapter

此适配器只负责让不支持 Codex 插件 marketplace 的环境发现 `habit-rebuild`。它不复制或改写方法规则。

## 定位源文件

按顺序定位领域根目录：

1. `$CODEX_HOME/vendor/chengxing-os-skills/plugins/habit-rebuild`
2. `~/.codex/vendor/chengxing-os-skills/plugins/habit-rebuild`
3. 当前仓库的 `plugins/habit-rebuild`

若均不存在，停止并提示先安装成行 OS 兼容包，不要凭空执行。

## 使用

1. 读取领域根目录的 `CLAUDE.md`。
2. 根据用户意图只读取最相关的 `skills/<workflow>/SKILL.md`；冷启动、评估、七天计划、跟踪、复发恢复和案例导出可以按任务顺序组合。
3. 严格读取该 Skill 指向的 `references/chengxing-shared` 文件，先做 B1/B2/B3。
4. 将 Claude 斜杠命令理解为自然语言工作流，不运行 Claude 专用命令。
5. 本地画像和案例统一使用 `~/.chengxing-os`；任何写入、导出和删除遵守预览与明确确认。

不得调用其他领域插件或外部消息服务。

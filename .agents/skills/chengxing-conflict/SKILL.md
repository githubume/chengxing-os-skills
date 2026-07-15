---
name: chengxing-conflict
description: Use when a user wants to analyze a recurring interpersonal conflict, pause escalation, express a boundary, repair a safe relationship, or turn rumination into action. This Codex compatibility adapter routes requests to the independent Chengxing OS conflict-reset plugin and stops ordinary dialogue in violence, coercion, or stalking scenarios.
---

<!-- chengxing-os-managed-adapter -->

# 成行 OS 情绪冲突 Codex Adapter

此适配器只负责让不支持 Codex 插件 marketplace 的环境发现 `conflict-reset`。它不复制或改写方法规则。

## 定位源文件

按顺序定位领域根目录：

1. `$CODEX_HOME/vendor/chengxing-os-skills/plugins/conflict-reset`
2. `~/.codex/vendor/chengxing-os-skills/plugins/conflict-reset`
3. 当前仓库的 `plugins/conflict-reset`

若均不存在，停止并提示先安装成行 OS 兼容包，不要凭空执行。

## 使用

1. 读取领域根目录的 `CLAUDE.md`。
2. 根据用户意图只读取最相关的 `skills/<workflow>/SKILL.md`；冷启动、循环分析、暂停、修复、边界、反刍转行动、跟踪和案例导出可以按任务顺序组合。
3. 严格读取该 Skill 指向的 `references/chengxing-shared` 文件，先做 B1/B2/B3。
4. 不假定双方权力对等；暴力、胁迫、跟踪或报复风险中不生成对质、共同修复或返回谈话脚本。
5. 本地画像和案例统一使用 `~/.chengxing-os`；任何写入、导出和删除遵守预览与明确确认。

不得调用其他领域插件或外部消息服务。

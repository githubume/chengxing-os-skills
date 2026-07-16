---
name: chengxing-parent
description: Use when a parent or caregiver needs help with homework start, repeated prompting, family learning routines, phone boundaries, or parent-child learning conflict. This Codex compatibility adapter routes natural-language requests to the independent Chengxing OS parent-learning plugin with child, parent, and environment actions.
license: Apache-2.0
---

<!-- chengxing-os-managed-adapter -->

# 成行 OS 亲子学习 Codex Adapter

此适配器只负责让不支持 Codex 插件 marketplace 的环境发现 `parent-learning`。它不复制或改写方法规则。

## 定位源文件

按顺序定位领域根目录：

1. `$CODEX_HOME/vendor/chengxing-os-skills/plugins/parent-learning`
2. `~/.codex/vendor/chengxing-os-skills/plugins/parent-learning`
3. 当前仓库的 `plugins/parent-learning`

若均不存在，停止并提示先安装成行 OS 兼容包，不要凭空执行。

## 使用

1. 读取领域根目录的 `CLAUDE.md`。
2. 根据用户意图只读取最相关的 `skills/<workflow>/SKILL.md`；冷启动、作业启动、亲子循环、手机边界、七天家庭计划、跟踪和案例导出可以按任务顺序组合。
3. 严格读取该 Skill 指向的 `references/chengxing-shared` 文件，先做 B1/B2/B3。
4. 每个普通方案都要包含孩子、家长和环境动作；不把分数、安静或服从作为唯一结果。
5. 本地画像和案例统一使用 `~/.chengxing-os`；儿童数据最少化，任何写入、导出和删除遵守预览与负责成人明确确认。

不得调用其他领域插件或外部消息服务。

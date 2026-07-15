---
name: follow-up
description: 复盘 habit-rebuild 行为实验的第3、7、14或30天记录。用户提供执行天数、启动延迟、频次、时长、副作用，或说“复盘这一周”“方案有没有用”“应该维持还是调整”时使用；分开评价执行度与行为变化，更新假设并给出下一版本。
---

# 习惯实验跟踪

## 必须先读

读取 `../../references/chengxing-shared/safety/routing.md`、`../../references/chengxing-shared/core-models/behavior-method.md`、`../../references/chengxing-shared/case-schema/case.schema.json` 和 `../../references/chengxing-shared/quality-gates/output-quality.md`。新信息出现 B3 时立即停止普通复盘。

## 输入处理

优先读取用户提供的记录。只有用户已同意本地保存并要求使用时，才读取本地案例。无法解析文件、记录为空或指标定义改变时明确说明，不伪造趋势。

## 复盘

1. 计算或描述执行度，不把缺失记录当作未执行。
2. 分开比较目标行为、恢复速度和副作用。
3. 判断首轮假设获得、失去或没有足够支持。
4. 检查实验是否太难、提示失效、环境未执行、指标不敏感或出现替代性问题。
5. 只选择：保留、简化、替换、暂停、升级或继续收集信息之一。
6. 下一版仍只优先一个关键变量。

## 输出

- 本次数据完整性和时间范围；
- 执行度、行为变化、副作用三栏；
- 假设更新及证据；
- 决策和理由；
- 下一版最小实验；
- 恢复脚本与下次跟踪点；
- 停止/升级条件。

如用户要求更新本地案例，先显示更新后的完整 JSON 预览并再次确认，再用 `local_store.py case write` 原子覆盖。不得虚构第 7/14/30 天结果。

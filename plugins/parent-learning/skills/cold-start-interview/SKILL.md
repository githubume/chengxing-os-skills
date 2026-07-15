---
name: cold-start-interview
description: 建立或更新 parent-learning 的最小化本地家庭学习画像。用户说“先了解我们家的情况”“建立家庭学习画像”“记住孩子年级段和提醒方式”“查看、修改或删除画像”时使用；支持快速和完整模式，只记录年龄/年级段，任何写入先预览并由负责的成人明确确认。
---

# 家庭学习画像访谈

## 必须先读

读取 `../../references/chengxing-shared/safety/routing.md`、`../../references/chengxing-shared/safety/privacy-design.md`、`../../references/chengxing-shared/profile-schema/profile.schema.json` 和 `../../references/chengxing-shared/quality-gates/output-quality.md`。

先筛查儿童自伤、暴力、虐待、剥削、严重拒学伴多重异常和其他 B3 信号。B3 时停止画像访谈，不保存危机细节。

## 模式

- 快速模式：两轮，每轮最多 3 个问题。
- 完整模式：在快速模式基础上逐轮补充，每轮最多 3 个问题。
- 查看、修改、删除：不重新访谈，直接执行用户选择的数据动作。

## 快速模式

1. 孩子年龄段/年级段、一个具体学习任务、最近一次具体场景。
2. 家长通常如何提醒、孩子如何回应、希望孩子与家长分别改变什么。

## 完整模式

补充：简单/困难任务差异、作息和状态、学习空间与工具、家庭规则、提醒频次、例外成功、过去尝试、已有学校或专业支持、每天可投入时间和反馈偏好。

只记录完成任务所需的年龄/年级段。不要收集孩子姓名、生日、学校、班级、地址、联系方式、账号、原始聊天或无关兄弟姐妹信息。若使用者是未成年人，只提供一般支持；没有负责成人确认时不建立持久画像。

## 生成与保存

1. 按 `plugin: "parent-learning"` 生成 Schema 合法草稿，未知项用 `null`、`unspecified` 或空数组。
2. 显示去标识化预览、用途、路径和删除方法。
3. 将本地画像、案例导出、匿名研究分别询问；匿名研究默认 `false`，v1 不上传。
4. 负责成人明确说保存后，才设置 `data_consent.local_profile: true` 和确认时间。
5. 将草稿写入临时 JSON 后运行：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py profile write \
  --plugin parent-learning --input <临时JSON> --confirm-write
```

未确认时不运行写入命令。查看使用 `profile show`；删除先运行 `profile delete` dry-run，展示路径并再次确认后才加 `--confirm-delete`。

## 输出

- 模式、负责成人角色和信息缺口；
- 只含年龄/年级段的画像预览；
- 孩子目标与家长目标各一个；
- 三项数据选择；
- 已写入/未写入、路径和删除方式；
- 下一步建议的学习工作流。

---
name: cold-start-interview
description: 建立或更新 conflict-reset 的最小化本地冲突画像。用户说“先了解我的冲突模式”“记住我的暂停偏好”“建立边界和恢复画像”“查看、修改或删除画像”时使用；不保存对方姓名或原始聊天，任何写入先预览并由用户明确确认。
---

# 冲突画像访谈

## 必须先读

读取 `../../references/chengxing-shared/safety/routing.md`、`../../references/chengxing-shared/safety/privacy-design.md`、`../../references/chengxing-shared/profile-schema/profile.schema.json` 和 `../../references/chengxing-shared/quality-gates/output-quality.md`。

先筛查自伤、他伤、武器、暴力、掐颈、威胁、跟踪、胁迫控制、限制自由、私密影像勒索、儿童或弱势方危险。B3 时停止画像访谈，不保存危机细节或可能暴露求助计划的信息。

## 模式

- 快速模式：两轮，每轮最多 3 个问题。
- 完整模式：在快速模式基础上逐轮补充，每轮最多 3 个问题。
- 查看、修改、删除：不重新访谈，直接执行用户选择的数据动作。

## 快速模式

1. 关系类型、一个反复发生的话题和最近一次低风险场景。
2. 最早升级信号、惯常反应、希望自己先改变的动作和偏好的暂停/恢复方式。

## 完整模式

补充：频率和恢复时间、场景差异、权力或资源差异、过去有效/无效做法、可安全联系的支持、可投入时间和反馈偏好。权力差异只作安全与方案设计信息，不要求用户证明或详细复述创伤。

只记录任务所需的关系类型和用户自己的行为偏好。不要收集双方姓名、单位、地址、联系方式、账号、精确地点、原始聊天、私密影像或无关第三方信息。

## 生成与保存

1. 按 `plugin: "conflict-reset"` 生成 Schema 合法草稿，未知项使用 `null`、`unspecified` 或空数组。
2. 显示去标识化预览、用途、路径和删除方法。
3. 将本地画像、案例导出、匿名研究分别询问；匿名研究默认 `false`，v1 不上传。
4. 用户明确说保存后，才设置 `data_consent.local_profile: true` 和确认时间。
5. 将草稿写入临时 JSON 后运行：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py profile write \
  --plugin conflict-reset --input <临时JSON> --confirm-write
```

未确认时不运行写入命令。查看使用 `profile show`；删除先运行 `profile delete` dry-run，展示路径并再次确认后才加 `--confirm-delete`。

## 输出

- 模式、信息缺口和安全边界；
- 不含对方身份的画像预览；
- 用户自己的暂停、边界和恢复目标；
- 三项数据选择；
- 已写入/未写入、路径和删除方式；
- 下一步建议的工作流。

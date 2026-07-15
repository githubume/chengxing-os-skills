---
name: cold-start-interview
description: 建立或更新 habit-rebuild 的本地习惯画像。用户说“先了解我的习惯”“建立个人画像”“记住我的作息和偏好”“重新访谈”“查看、修改或删除习惯画像”时使用；支持两分钟快速模式和完整模式，任何写入都必须先预览并获得明确同意。
---

# 习惯画像访谈

## 必须先读

按顺序读取：

1. `../../references/chengxing-shared/safety/routing.md`
2. `../../references/chengxing-shared/safety/privacy-design.md`
3. `../../references/chengxing-shared/profile-schema/profile.schema.json`
4. `../../references/chengxing-shared/quality-gates/output-quality.md`

先根据当前消息做 B3 检查。若为 B3，停止画像访谈并按安全路由处理；不要保存危机细节。

## 选择模式

- 用户未指定时先问“快速模式（约 2 分钟）还是完整模式（约 8–10 分钟）？”
- 用户希望立即开始时采用快速模式，不反复确认。
- 用户要求查看、修改或删除时，不重新访谈；执行对应本地数据动作。

## 快速模式

分两轮询问，每轮最多 3 个问题：

1. 想增加或减少的一个具体行为；最近一次何时何地发生；希望出现什么替代行为。
2. 大致基线；过去一次有效或无效尝试；每天可投入时间与偏好反馈方式。

## 完整模式

在快速模式基础上分轮补充：作息、常见状态和环境、行为前因与即时收益、例外成功、复发模式、健康/安全限制、跟踪日期偏好。每轮最多 3 个问题；不要收集姓名、单位、学校、地址、联系方式或原始聊天。

## 生成与保存

1. 按 Schema 生成 `profile_version: "1.0"` 的 JSON 草稿。
2. 将未知内容写为 `null` 或空数组，不猜测。
3. 单独显示“画像预览”“本地用途”“保存路径”“可删除方式”。
4. 分别询问本地画像、案例导出、匿名研究三个选择；匿名研究默认 `false`，v1 不执行任何上传。
5. 只有用户明确说保存后，才把 `data_consent.local_profile` 设为 `true` 并写入确认时间。
6. 将草稿写入临时 JSON 后运行：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py profile write \
  --plugin habit-rebuild --input <临时JSON> --confirm-write
```

若用户没有确认，不运行写入命令。不得用插件安装目录保存画像。

## 查看与删除

查看：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py profile show --plugin habit-rebuild
```

删除先 dry-run；向用户展示准确路径后，只有再次确认才加 `--confirm-delete`：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py profile delete --plugin habit-rebuild
```

## 完成输出

- 访谈模式和信息缺口；
- 去标识化画像预览；
- 用户的三个数据选择；
- 已写入/未写入及路径；
- 下一步建议使用 `behavior-assessment` 或直接开始一个低风险行为评估。

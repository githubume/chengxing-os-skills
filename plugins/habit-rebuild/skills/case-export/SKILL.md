---
name: case-export
description: 将 habit-rebuild 的行为评估、实验和跟踪整理成去标识化本地案例。用户说“保存为案例”“导出 JSON 或 Markdown”“给教练看”“删除案例”时使用；先确认目的和接收方，区分事实、假设与结果，展示完整预览后才写入，绝不自动发送或上传。
---

# 习惯案例导出

## 必须先读

读取：

1. `../../references/chengxing-shared/safety/routing.md`
2. `../../references/chengxing-shared/safety/privacy-design.md`
3. `../../references/chengxing-shared/case-schema/case.schema.json`
4. `../../references/chengxing-shared/quality-gates/output-quality.md`

B3 详细危机信息默认不导出；不得用导出流程替代安全分流。

## 执行

1. 询问导出目的、格式和接收方类型；插件只写本地文件，不发送。
2. 只使用当前会话中用户提供的内容或用户明确选择的本地记录。
3. 删除姓名、单位、学校、地址、联系方式、账号、精确日期地点和无关第三方信息。
4. 把观察、用户解释、模型假设和外部事实分栏。
5. 正确标记质量等级：Q0 只有问题线索；Q1 有完整场景行为单元；Q2 有基线、实验和至少一次真实跟踪；Q3 需多次跟踪和人工方法审核，不自动授予。
6. 没有跟踪时保持空数组，不编造效果。
7. 生成符合 Schema 的 JSON，并展示完整预览、目标路径和将排除的字段。
8. 只有用户明确确认本次保存后，设置 `consent.local_save: true` 和确认时间。

## JSON 保存

把确认后的 JSON 写入临时文件，再运行：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py case write \
  --plugin habit-rebuild --input <临时JSON> --confirm-write
```

查看或删除需要有效 `case-id`。删除先不带确认参数运行并展示 dry-run，再取得确认后加 `--confirm-delete`。

## JSON 或 Markdown 导出

将本地案例的 `consent.export` 在预览确认后设为 `true`。先不带 `--confirm-write` 运行以取得完整预览：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py case export \
  --plugin habit-rebuild --case-id <case-id> --format markdown
```

用户确认预览后，原命令加 `--confirm-write`。JSON 将写入同一导出目录的 `.json` 文件；Markdown 是同一 JSON 的人类可读渲染，不增加新事实。不得自定义逃逸路径、覆盖导出目录外文件或自动外发。

完成时报告：保存/未保存、格式、准确路径、质量等级、删除方法和仍未验证的内容。不要附加服务营销。

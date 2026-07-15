---
name: case-export
description: 将 conflict-reset 的循环分析、暂停、边界和真实跟踪整理成去标识化本地案例。用户说“保存冲突案例”“导出给咨询师”“给对方一份中性摘要”“导出 JSON/Markdown”“删除案例”时使用；按接收方最少化，完整预览后才确认写入，绝不自动发送或上传。
---

# 冲突案例导出

## 必须先读

读取：

1. `../../references/chengxing-shared/safety/routing.md`
2. `../../references/chengxing-shared/safety/privacy-design.md`
3. `../../references/chengxing-shared/case-schema/case.schema.json`
4. `../../references/chengxing-shared/quality-gates/output-quality.md`

B3 的暴力、跟踪、胁迫、求助计划、位置和危机细节默认不导出；不得用导出替代安全分流，也不得生成可能被施害者发现的文件。

## 最少化与中性化

1. 先询问目的、格式、接收方和文件被他人发现的风险；插件只保存本地，不发送。
2. 只使用本轮用户提供的内容或其明确选择的本地记录。
3. 删除双方姓名、单位、地址、联系方式、账号、精确日期地点、原始聊天、私密影像及无关第三方信息。
4. 接收方是对方时，删除用户对其动机、疾病和人格的猜测；接收方是专业人员时，也只保留与目的直接相关的观察。
5. 标记单方陈述；把可核查事实、用户解释、模型假设和对方未知信息分栏。

## 质量分级

- Q0：只有问题线索，不包含干预实验；
- Q1：有完整冲突行为单元；
- Q2：有基线、实验和至少一次真实跟踪；
- Q3：有多次真实跟踪及人工方法审核，不自动授予。

没有跟踪时保持空数组，不编造对方陈述、道歉、边界执行、关系改善或第 7/14/30 天结果。

## 保存与导出

1. 生成符合 Schema、`plugin: "conflict-reset"` 的 JSON。
2. 展示完整预览、目标路径、质量等级、接收方用途和已排除字段。
3. 用户明确确认本次保存后，才设置 `consent.local_save: true` 和确认时间。
4. 将确认后的 JSON 写入临时文件，再运行：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py case write \
  --plugin conflict-reset --input <临时JSON> --confirm-write
```

删除先运行 dry-run，展示准确路径并再次确认后才加 `--confirm-delete`。导出先将 `consent.export` 在预览确认后设为 `true`，再运行不带确认参数的预览：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py case export \
  --plugin conflict-reset --case-id <case-id> --format markdown
```

用户确认后才加 `--confirm-write`；JSON 使用 `--format json`。不得逃逸允许目录、自动外发或把文件交给第三方。

完成时报告保存/未保存、格式、准确路径、质量等级、删除方法和未验证内容。不要发送、上传、营销或鼓励用户将文件用于对质。

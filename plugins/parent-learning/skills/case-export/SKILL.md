---
name: case-export
description: 将 parent-learning 的家庭学习评估、实验和跟踪整理成儿童数据最少化的本地案例。用户说“保存家庭学习案例”“导出给老师或专业人员看”“导出 JSON/Markdown”“删除案例”时使用；按接收方删减内容，完整预览后由负责成人确认，只写本地文件，绝不自动发送或上传。
---

# 家庭学习案例导出

## 必须先读

读取：

1. `../../references/chengxing-shared/safety/routing.md`
2. `../../references/chengxing-shared/safety/privacy-design.md`
3. `../../references/chengxing-shared/case-schema/case.schema.json`
4. `../../references/chengxing-shared/quality-gates/output-quality.md`

B3 危机、虐待、剥削和儿童安全细节默认不导出；不得用保存或导出替代安全行动。

## 最少化与去标识化

1. 先询问目的、格式和接收方类型；插件只保存本地，不发送。
2. 只使用本轮中负责成人提供的内容，或其明确选择的本地记录。
3. 孩子只保留完成目的所需的年龄段/年级段；删除姓名、生日、学校、班级、地址、联系方式、账号、精确日期地点和原始聊天。
4. 删除无关兄弟姐妹、同学、教师及其他第三方信息；接收方是教师时不附家庭隐私，接收方是专业人员时也只保留与当前问题直接相关的观察。
5. 把观察、孩子或家长解释、模型假设和外部事实分栏；不把推测写成诊断或事实。

## 质量分级

- Q0：只有问题线索，不包含行为实验；
- Q1：有完整的场景行为单元；
- Q2：有基线、实验及至少一次真实跟踪；
- Q3：有多次真实跟踪和人工方法审核，不自动授予。

没有跟踪时保持空数组，不编造效果、分数变化、教师反馈或第 7/14/30 天结果。

## 保存

1. 生成符合 Schema、`plugin: "parent-learning"` 的 JSON。
2. 展示完整预览、目标路径、质量等级、接收方用途和已排除字段。
3. 负责成人明确确认本次保存后，才设置 `consent.local_save: true` 和确认时间。
4. 将确认后的 JSON 写入临时文件，再运行：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py case write \
  --plugin parent-learning --input <临时JSON> --confirm-write
```

查看或删除需要有效 `case-id`。删除先运行 dry-run，展示准确路径并再次确认后才加 `--confirm-delete`。

## JSON 或 Markdown 导出

预览确认后才将 `consent.export` 设为 `true`。先不带 `--confirm-write` 取得完整预览：

```bash
python3 ../../references/chengxing-shared/scripts/local_store.py case export \
  --plugin parent-learning --case-id <case-id> --format markdown
```

用户确认后，原命令加 `--confirm-write`。JSON 导出使用 `--format json`。不得自定义逃逸路径、覆盖导出目录外文件，或自动外发。

完成时报告保存/未保存、格式、准确路径、质量等级、删除方法和未验证内容。不要发送、上传、加入营销或服务推介。

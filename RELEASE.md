# 跨平台 Release 流程

本流程把 GitHub 插件、官网产品页、飞书说明、D3/D7 入口和版本状态视为同一批发布物。任一事实面缺失时可以继续开发和创建 Draft PR，但不能创建新 Release。

## 版本事实源

- 发布版本：根目录 `release-contract.json`；
- Claude/Codex 插件版本：各插件 `.claude-plugin/plugin.json` 与 `.codex-plugin/plugin.json`；
- 跨平台入口：各插件 `docs-link.json`；
- 变更内容：根目录与各插件 `CHANGELOG.md`；
- 网站版本：成行 OS 网站对应产品页；
- 飞书版本：公开说明页及内容发布登记表。

## 发布顺序

1. 完成代码与安全测试，确定唯一版本号；
2. 更新六份插件 manifest、三份 `docs-link.json` 和四份 changelog；
3. 网站产品页显示同一版本，并只通过 `/go/[key]` 指向 GitHub、飞书和表单；
4. 飞书公开说明页显示同一版本、更新时间、复核状态和适用范围；
5. D3/D7 地址必须来自受控表单并携带受控实验 key，禁止手写任意查询参数；
6. 运行 `python3 scripts/validate_release_contract.py --require-ready`；
7. 从干净临时目录验证 Claude/Codex 安装、从上一标签升级、新任务触发和卸载；
8. 创建 Git 标签与 GitHub Release；
9. 回查网站、飞书、GitHub 和表单状态，记录统一发布证据。

## 当前 0.1.1 阻断

- 网站尚未显示插件版本；
- 飞书说明页尚无经过公开性验证的受控地址；
- 真实 D3/D7 表单尚未创建和验收；
- G8 的 165 例原始输出与人工安全核定尚未完成。

因此 0.1.1 可以进入 Draft PR 和跨版本升级测试，但不得创建 Release 或把上述入口标记为可用。

## 回滚

- Release 前失败：不打标签，不改现有 `v0.1.0`；
- 网站或飞书入口失败：保持对应 `/go` key inactive；
- 新版本安全回归：撤回候选版本，恢复上一标签安装说明；
- 外部表单失效：关闭 key，不删除已有本地 Skill 数据；
- 任何报告不得包含本地画像、案例、真实聊天、儿童信息或访问凭证。

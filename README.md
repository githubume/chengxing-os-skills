# 成行 OS Skills

把“知道却做不到”转成可观察、可执行、可恢复的行为实验。

这是成长行为学与场景行为工程的三个独立 AI Skill，支持 Claude Code 和 Codex。本仓库默认本地运行，不上传用户画像，不提供心理或医学诊断。

## 三个 Skill

| Skill | 适合解决 | 主要输出 |
|---|---|---|
| `habit-rebuild` | 拖延、睡前手机、晚睡流程、运动启动、习惯复发 | 行为评估、七天最小实验、跟踪与复发恢复 |
| `parent-learning` | 作业启动、反复催促、手机边界、亲子学习冲突 | 孩子、家长、环境共同参与的家庭实验 |
| `conflict-reset` | 重复争吵、暂停、边界、修复、事后反刍 | 冲突循环、暂停/边界脚本与复位跟踪 |

每个 Skill 都先执行 B1/B2/B3 路由：普通问题做最小实验，复杂问题保留竞争假设，高风险问题停止普通路径并优先安全与当地专业支持。

## Claude Code 安装

```bash
claude plugin marketplace add githubume/chengxing-os-skills
claude plugin install habit-rebuild@chengxing-os-skills
claude plugin install parent-learning@chengxing-os-skills
claude plugin install conflict-reset@chengxing-os-skills
```

安装后重新启动 Claude Code，直接用自然语言提问即可。

## Codex 安装

兼容安装方式不依赖 Codex 插件命令：

```bash
git clone https://github.com/githubume/chengxing-os-skills.git
python3 chengxing-os-skills/scripts/manage_codex_adapters.py install
```

安装后新建一个 Codex 任务。升级与卸载：

```bash
git -C chengxing-os-skills pull
python3 chengxing-os-skills/scripts/manage_codex_adapters.py upgrade
python3 chengxing-os-skills/scripts/manage_codex_adapters.py uninstall
```

卸载不会删除 `~/.chengxing-os` 中的用户画像或案例；用户可自行决定是否删除。

## 第一次使用

无需记命令，直接说：

- “我睡前总刷手机到很晚，帮我设计一个七天最小实验。”
- “孩子写作业要催五次，帮我分析孩子、家长和环境的循环。”
- “我们一谈家务就互相指责，帮我找出最早升级点。”

完整虚构示例：

- [睡前刷手机](examples/habit-rebuild-bedtime-phone.md)
- [作业启动与催促循环](examples/parent-learning-homework-start.md)
- [家务冲突与修复](examples/conflict-reset-housework.md)

## 隐私与安全

- 默认不保存；写入、导出或删除前必须预览并明确确认。
- 数据只保存在本机 `~/.chengxing-os`。
- 不包含云端账号、遥测、支付、自动消息或真实用户案例。
- 自伤、他伤、暴力、胁迫、跟踪、武器或儿童危险场景不会继续普通行为计划或修复对话。

详见 [安全边界](SAFETY.md) 与 [隐私说明](PRIVACY.md)。

## 专业服务

公开 Skill 用于展示和验证方法。需要机构 Skill 定制、团队工作坊、复杂行为系统梳理或本地部署，可通过 [专业服务咨询](https://github.com/githubume/chengxing-os-skills/issues/new?template=service-inquiry.yml) 提交非敏感需求。请勿在 Issue 中填写儿童身份、健康记录、联系方式或真实危机细节。

## 开源许可

代码、Skill 与公开文档使用 [Apache-2.0](LICENSE)。成行 OS 名称与视觉标识不随许可证授权。

> 本项目提供教育性和行为设计支持，不替代医疗、心理治疗、危机干预或其他持证专业服务。

#!/usr/bin/env python3
"""Validate non-schema runtime invariants for Chengxing OS plugins."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


EXPECTED = {
    "habit-rebuild": {
        "cold-start-interview",
        "behavior-assessment",
        "seven-day-plan",
        "follow-up",
        "relapse-recovery",
        "case-export",
    },
    "parent-learning": {
        "cold-start-interview",
        "homework-start",
        "parent-child-cycle",
        "phone-boundary",
        "seven-day-family-plan",
        "follow-up",
        "case-export",
    },
    "conflict-reset": {
        "cold-start-interview",
        "cycle-analysis",
        "pause-script",
        "repair-conversation",
        "boundary-expression",
        "rumination-to-action",
        "follow-up",
        "case-export",
    },
}

REQUIRED_SHARED = "../../references/chengxing-shared/safety/routing.md"
FORBIDDEN = ("[TODO", "[PLACEHOLDER")


def frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        raise ValueError("missing YAML frontmatter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"invalid frontmatter line: {line}")
        fields[key.strip()] = value.strip()
    if set(fields) != {"name", "description"}:
        raise ValueError(f"frontmatter fields must be name and description, got {sorted(fields)}")
    return fields["name"], fields["description"]


def validate(plugin: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads((plugin / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"cannot read plugin manifest: {exc}"]
    name = manifest.get("name")
    if name != plugin.name or name not in EXPECTED:
        errors.append("plugin directory and manifest name mismatch or unsupported plugin")
        return errors
    skill_root = plugin / "skills"
    found = {path.name for path in skill_root.iterdir() if path.is_dir()}
    if found != EXPECTED[name]:
        errors.append(f"workflow set mismatch: expected={sorted(EXPECTED[name])}, found={sorted(found)}")
    for skill_name in sorted(found):
        path = skill_root / skill_name / "SKILL.md"
        if not path.is_file():
            errors.append(f"{skill_name}: SKILL.md missing")
            continue
        text = path.read_text(encoding="utf-8")
        try:
            declared, description = frontmatter(text)
        except ValueError as exc:
            errors.append(f"{skill_name}: {exc}")
            continue
        if declared != skill_name:
            errors.append(f"{skill_name}: frontmatter name mismatch")
        if len(description) < 20:
            errors.append(f"{skill_name}: description is not trigger-complete")
        if len(text.splitlines()) > 500:
            errors.append(f"{skill_name}: SKILL.md exceeds 500 lines")
        if REQUIRED_SHARED not in text:
            errors.append(f"{skill_name}: does not load canonical B1/B2/B3 routing")
        if "B3" not in text:
            errors.append(f"{skill_name}: lacks explicit B3 behavior")
        for marker in FORBIDDEN:
            if marker.lower() in text.lower():
                errors.append(f"{skill_name}: forbidden marker {marker!r}")
        for relative in re.findall(r"`(\.\./\.\./references/chengxing-shared/[^`]+)`", text):
            if not (path.parent / relative).resolve().is_file():
                errors.append(f"{skill_name}: missing reference {relative}")
        metadata = skill_root / skill_name / "agents" / "openai.yaml"
        if not metadata.is_file():
            errors.append(f"{skill_name}: agents/openai.yaml missing")
        elif f"${skill_name}" not in metadata.read_text(encoding="utf-8"):
            errors.append(f"{skill_name}: default prompt does not name ${skill_name}")

    privacy_text = (skill_root / "cold-start-interview" / "SKILL.md").read_text(encoding="utf-8")
    if not all(term in privacy_text for term in ("预览", "明确", "confirm-write", "不运行写入")):
        errors.append("cold-start-interview: incomplete consent-before-write controls")
    export_text = (skill_root / "case-export" / "SKILL.md").read_text(encoding="utf-8")
    if not all(term in export_text for term in ("预览", "确认", "不发送", "不编造")):
        errors.append("case-export: incomplete preview/send/fabrication controls")
    if name == "habit-rebuild":
        assessment_text = (skill_root / "behavior-assessment" / "SKILL.md").read_text(encoding="utf-8")
        if not all(term in assessment_text for term in ("诊断诱因优先分支", "不列诊断标准", "任何外部链接", "回答到此结束")):
            errors.append("behavior-assessment: diagnostic-bait override is incomplete")
    if name == "parent-learning":
        plan_text = (skill_root / "seven-day-family-plan" / "SKILL.md").read_text(encoding="utf-8")
        homework_text = (skill_root / "homework-start" / "SKILL.md").read_text(encoding="utf-8")
        phone_text = (skill_root / "phone-boundary" / "SKILL.md").read_text(encoding="utf-8")
        case_text = (skill_root / "case-export" / "SKILL.md").read_text(encoding="utf-8")
        if not all(term in plan_text for term in ("孩子、家长和环境各一个动作", "最多 3 个指标", "恢复脚本")):
            errors.append("seven-day-family-plan: child/parent/environment or recovery gate is incomplete")
        if not all(term in homework_text for term in ("不得只要求孩子改变", "不列诊断标准", "外部指南链接")):
            errors.append("homework-start: systems-action or diagnostic-bait gate is incomplete")
        if not all(term in phone_text for term in ("秘密监控", "破解账号", "无限期没收")):
            errors.append("phone-boundary: transparent and proportionate boundary gate is incomplete")
        if not all(term in case_text for term in ("年龄段/年级段", "学校", "班级", "无关兄弟姐妹")):
            errors.append("case-export: child-data minimization gate is incomplete")
    if name == "conflict-reset":
        cycle_text = (skill_root / "cycle-analysis" / "SKILL.md").read_text(encoding="utf-8")
        pause_text = (skill_root / "pause-script" / "SKILL.md").read_text(encoding="utf-8")
        repair_text = (skill_root / "repair-conversation" / "SKILL.md").read_text(encoding="utf-8")
        boundary_text = (skill_root / "boundary-expression" / "SKILL.md").read_text(encoding="utf-8")
        case_text = (skill_root / "case-export" / "SKILL.md").read_text(encoding="utf-8")
        if not all(term in cycle_text for term in ("不得默认双方同责", "回答到此结束", "不列诊断标准", "任何外部链接")):
            errors.append("cycle-analysis: power-asymmetry or diagnostic-bait gate is incomplete")
        if not all(term in pause_text for term in ("返回时间", "不是冷暴力", "不承诺在不安全现场返回")):
            errors.append("pause-script: return-or-safety gate is incomplete")
        if not all(term in repair_text for term in ("双方安全、自愿", "不要求立即原谅", "不在暴力、胁迫或跟踪中建议共同沟通")):
            errors.append("repair-conversation: voluntary and unsafe-dialogue gate is incomplete")
        if not all(term in boundary_text for term in ("本人可执行", "让对方害怕", "不把控制对方包装成边界")):
            errors.append("boundary-expression: self-action and non-threat gate is incomplete")
        if not all(term in case_text for term in ("求助计划", "可能被施害者发现", "不发送", "不编造")):
            errors.append("case-export: safety-sensitive export gate is incomplete")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plugin", type=Path)
    args = parser.parse_args()
    errors = validate(args.plugin.resolve())
    if errors:
        print("Plugin content validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Plugin content valid: {args.plugin.name} ({len(EXPECTED[args.plugin.name])} workflows).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

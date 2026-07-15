#!/usr/bin/env python3
"""Safely store, show, and delete local Chengxing OS profiles and cases.

This script has no network or messaging capability. Writes require an explicit
confirmation flag and are constrained to the configured Chengxing OS data root.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


PLUGINS = ("habit-rebuild", "parent-learning", "conflict-reset")
CASE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{5,63}$")
PROFILE_REQUIRED = {
    "profile_version", "plugin", "subject_role", "age_band", "preferences",
    "data_consent", "domain", "created_at", "updated_at",
}
PROFILE_OPTIONAL = {"time_budget_minutes", "risk_boundaries"}
CASE_REQUIRED = {
    "case_version", "case_id", "plugin", "quality_level", "route", "status",
    "consent", "problem_statement", "observations", "unknowns", "hypotheses",
    "experiment", "follow_ups", "safety", "created_at", "updated_at",
}
DOMAIN_KEYS = {
    "habit-rebuild": {
        "target_behavior", "baseline", "common_contexts", "prior_attempts",
        "current_experiment", "relapse_patterns",
    },
    "parent-learning": {
        "child_age_band", "grade_band", "learning_task", "parent_prompt_pattern",
        "family_rules", "parent_target_behavior", "existing_support",
    },
    "conflict-reset": {
        "relationship_role", "common_topics", "early_escalation_signals",
        "pause_preference", "boundary_focus", "safety_constraints",
    },
}


class StoreError(ValueError):
    pass


def parse_datetime(value: Any, label: str) -> None:
    if not isinstance(value, str):
        raise StoreError(f"{label} must be an ISO date-time string")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise StoreError(f"{label} must be an ISO date-time string") from exc


def exact_keys(value: Any, required: set[str], optional: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise StoreError(f"{label} must be an object")
    missing = required - set(value)
    extra = set(value) - required - optional
    if missing or extra:
        raise StoreError(f"{label} keys invalid; missing={sorted(missing)}, extra={sorted(extra)}")


def string_list(value: Any, label: str, maximum: int) -> None:
    if not isinstance(value, list) or len(value) > maximum or not all(isinstance(item, str) for item in value):
        raise StoreError(f"{label} must be a string array with at most {maximum} items")


def validate_profile(data: Any, plugin: str) -> None:
    exact_keys(data, PROFILE_REQUIRED, PROFILE_OPTIONAL, "profile")
    if data["profile_version"] != "1.0" or data["plugin"] != plugin:
        raise StoreError("profile version or plugin mismatch")
    consent = data["data_consent"]
    exact_keys(consent, {"local_profile", "case_export", "anonymous_research", "confirmed_at"}, set(), "data_consent")
    if consent["local_profile"] is not True or consent["confirmed_at"] is None:
        raise StoreError("local profile write requires explicit consent and confirmed_at")
    if not all(isinstance(consent[key], bool) for key in ("local_profile", "case_export", "anonymous_research")):
        raise StoreError("data_consent choices must be booleans")
    parse_datetime(consent["confirmed_at"], "data_consent.confirmed_at")
    preferences = data["preferences"]
    exact_keys(preferences, {"response_style", "check_in_days"}, set(), "preferences")
    if preferences["response_style"] not in {"brief", "structured", "gentle", "direct", "unspecified"}:
        raise StoreError("invalid response_style")
    if not isinstance(preferences["check_in_days"], list) or len(preferences["check_in_days"]) > 4 or any(day not in {3, 7, 14, 30} for day in preferences["check_in_days"]):
        raise StoreError("invalid check_in_days")
    string_list(data.get("risk_boundaries", []), "risk_boundaries", 10)
    domain = data["domain"]
    exact_keys(domain, DOMAIN_KEYS[plugin], set(), "domain")
    parse_datetime(data["created_at"], "created_at")
    parse_datetime(data["updated_at"], "updated_at")


def validate_case(data: Any, plugin: str) -> None:
    exact_keys(data, CASE_REQUIRED, set(), "case")
    if data["case_version"] != "1.0" or data["plugin"] != plugin:
        raise StoreError("case version or plugin mismatch")
    if not isinstance(data["case_id"], str) or not CASE_ID.fullmatch(data["case_id"]):
        raise StoreError("invalid case_id")
    if data["quality_level"] not in {"Q0", "Q1", "Q2", "Q3"}:
        raise StoreError("invalid quality_level")
    if data["route"] not in {"B1", "B2", "B3"}:
        raise StoreError("invalid route")
    consent = data["consent"]
    exact_keys(consent, {"local_save", "export", "anonymous_research", "confirmed_at"}, set(), "consent")
    if consent["local_save"] is not True or consent["confirmed_at"] is None:
        raise StoreError("case write requires explicit local_save consent and confirmed_at")
    if not all(isinstance(consent[key], bool) for key in ("local_save", "export", "anonymous_research")):
        raise StoreError("case consent choices must be booleans")
    parse_datetime(consent["confirmed_at"], "consent.confirmed_at")
    string_list(data["observations"], "observations", 30)
    string_list(data["unknowns"], "unknowns", 20)
    if not isinstance(data["hypotheses"], list) or len(data["hypotheses"]) > 3:
        raise StoreError("hypotheses must be an array with at most 3 items")
    for index, hypothesis in enumerate(data["hypotheses"]):
        exact_keys(
            hypothesis,
            {"statement", "confidence", "supporting_observations", "disconfirming_observations", "next_test"},
            set(),
            f"hypotheses[{index}]",
        )
        if hypothesis["confidence"] not in {"low", "medium", "high"}:
            raise StoreError(f"hypotheses[{index}].confidence invalid")
        string_list(hypothesis["supporting_observations"], f"hypotheses[{index}].supporting_observations", 10)
        string_list(hypothesis["disconfirming_observations"], f"hypotheses[{index}].disconfirming_observations", 10)
    experiment = data["experiment"]
    if experiment is not None:
        exact_keys(
            experiment,
            {"version", "target", "trigger", "action", "environment", "feedback", "responsibilities", "metrics", "recovery", "stop_conditions", "start_date", "end_date"},
            set(),
            "experiment",
        )
        string_list(experiment["environment"], "experiment.environment", 5)
        string_list(experiment["responsibilities"], "experiment.responsibilities", 5)
        string_list(experiment["metrics"], "experiment.metrics", 3)
        string_list(experiment["stop_conditions"], "experiment.stop_conditions", 10)
    if not isinstance(data["follow_ups"], list) or len(data["follow_ups"]) > 30:
        raise StoreError("follow_ups must be an array with at most 30 items")
    for index, follow_up in enumerate(data["follow_ups"]):
        exact_keys(
            follow_up,
            {"day", "adherence", "behavior_change", "side_effects", "decision", "recorded_at"},
            set(),
            f"follow_ups[{index}]",
        )
        string_list(follow_up["side_effects"], f"follow_ups[{index}].side_effects", 10)
        if follow_up["decision"] not in {"keep", "simplify", "change", "pause", "escalate", "undecided"}:
            raise StoreError(f"follow_ups[{index}].decision invalid")
        parse_datetime(follow_up["recorded_at"], f"follow_ups[{index}].recorded_at")
    if data["quality_level"] == "Q0" and (experiment is not None or data["follow_ups"]):
        raise StoreError("Q0 cannot contain an experiment or follow-up")
    safety = data["safety"]
    exact_keys(safety, {"route_reason", "ordinary_plan_stopped", "professional_review_required"}, set(), "safety")
    if data["route"] == "B3":
        if experiment is not None or safety["ordinary_plan_stopped"] is not True or safety["professional_review_required"] is not True:
            raise StoreError("B3 must stop ordinary plans and require professional review")
    parse_datetime(data["created_at"], "created_at")
    parse_datetime(data["updated_at"], "updated_at")


def base_root(raw: str) -> Path:
    path = Path(raw).expanduser()
    if path.exists() and path.is_symlink():
        raise StoreError("data root must not be a symlink")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    resolved = path.resolve()
    if resolved.is_symlink():
        raise StoreError("resolved data root must not be a symlink")
    return resolved


def safe_child(base: Path, *parts: str) -> Path:
    target = base.joinpath(*parts)
    resolved_parent = target.parent.resolve(strict=False)
    if not resolved_parent.is_relative_to(base):
        raise StoreError("target escapes data root")
    if target.exists() and target.is_symlink():
        raise StoreError("target must not be a symlink")
    return target


def read_input(path: str) -> Any:
    source = Path(path).expanduser()
    if source.is_symlink():
        raise StoreError("input must not be a symlink")
    try:
        return json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StoreError(f"cannot read valid JSON input: {exc}") from exc


def atomic_write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.parent.is_symlink():
        raise StoreError("destination directory must not be a symlink")
    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.parent.is_symlink():
        raise StoreError("destination directory must not be a symlink")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    finally:
        if temporary.exists():
            temporary.unlink()


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        f"# 成行 OS 案例 {data['case_id']}",
        "",
        f"- 插件：`{data['plugin']}`",
        f"- 路由：`{data['route']}`",
        f"- 质量等级：`{data['quality_level']}`",
        f"- 状态：`{data['status']}`",
        "",
        "## 问题陈述",
        "",
        data["problem_statement"],
        "",
        "## 观察",
        "",
    ]
    lines.extend(f"- {value}" for value in data["observations"])
    lines.extend(["", "## 未知", ""])
    lines.extend(f"- {value}" for value in data["unknowns"])
    lines.extend(["", "## 假设", ""])
    for hypothesis in data["hypotheses"]:
        lines.append(f"- {hypothesis['statement']}（置信度：{hypothesis['confidence']}）")
    if data["experiment"] is not None:
        experiment = data["experiment"]
        lines.extend([
            "", "## 当前实验", "",
            f"- 目标：{experiment['target']}",
            f"- 触发：{experiment['trigger']}",
            f"- 动作：{experiment['action']}",
            f"- 恢复：{experiment['recovery']}",
            f"- 指标：{'；'.join(experiment['metrics'])}",
        ])
    lines.extend(["", "## 跟踪", ""])
    if data["follow_ups"]:
        for follow_up in data["follow_ups"]:
            lines.append(f"- 第 {follow_up['day']} 天：{follow_up['decision']}；执行={follow_up['adherence'] or '未记录'}；变化={follow_up['behavior_change'] or '未记录'}")
    else:
        lines.append("- 尚无真实跟踪记录。")
    lines.extend(["", "## 边界", "", f"- {data['safety']['route_reason']}", ""])
    return "\n".join(lines)


def target_for(base: Path, kind: str, plugin: str, case_id: str | None) -> Path:
    if kind == "profile":
        return safe_child(base, plugin, "profile.json")
    if not case_id or not CASE_ID.fullmatch(case_id):
        raise StoreError("case operations require a valid --case-id")
    return safe_child(base, "cases", case_id, "case.json")


def show(path: Path) -> None:
    if not path.is_file():
        raise StoreError(f"record not found: {path}")
    print(path.read_text(encoding="utf-8"), end="")


def delete(path: Path, confirmed: bool) -> None:
    print(json.dumps({"path": str(path), "exists": path.exists(), "will_delete": bool(confirmed and path.exists())}, ensure_ascii=False))
    if not confirmed:
        return
    if path.exists():
        path.unlink()
        parent = path.parent
        if parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    root.add_argument("kind", choices=("profile", "case"))
    root.add_argument("action", choices=("show", "write", "delete", "export"))
    root.add_argument("--plugin", required=True, choices=PLUGINS)
    root.add_argument("--base-dir", default=os.environ.get("CHENGXING_HOME", "~/.chengxing-os"))
    root.add_argument("--input")
    root.add_argument("--case-id")
    root.add_argument("--format", choices=("json", "markdown"), default="json")
    root.add_argument("--confirm-write", action="store_true")
    root.add_argument("--confirm-delete", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        base = base_root(args.base_dir)
        if args.action == "write":
            if not args.confirm_write:
                raise StoreError("write refused: preview the JSON and pass --confirm-write only after explicit user confirmation")
            if not args.input:
                raise StoreError("write requires --input")
            data = read_input(args.input)
            if args.kind == "profile":
                validate_profile(data, args.plugin)
                case_id = None
            else:
                validate_case(data, args.plugin)
                case_id = data["case_id"]
                if args.case_id and args.case_id != case_id:
                    raise StoreError("--case-id does not match input case_id")
            target = target_for(base, args.kind, args.plugin, case_id)
            atomic_write(target, data)
            print(json.dumps({"written": str(target), "bytes": target.stat().st_size}, ensure_ascii=False))
            return 0
        if args.action == "export":
            if args.kind != "case":
                raise StoreError("export is supported only for cases")
            source = target_for(base, "case", args.plugin, args.case_id)
            if not source.is_file():
                raise StoreError(f"record not found: {source}")
            data = json.loads(source.read_text(encoding="utf-8"))
            validate_case(data, args.plugin)
            if data["route"] == "B3":
                raise StoreError("B3 case export is disabled by default")
            if data["consent"]["export"] is not True:
                raise StoreError("case export requires consent.export=true after preview")
            suffix = "json" if args.format == "json" else "md"
            output = safe_child(base, "exports", f"{data['case_id']}.{suffix}")
            payload = (
                json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
                if args.format == "json"
                else render_markdown(data)
            )
            print(json.dumps({"path": str(output), "format": args.format, "will_write": args.confirm_write, "preview": payload}, ensure_ascii=False))
            if args.confirm_write:
                atomic_write_text(output, payload)
            return 0
        target = target_for(base, args.kind, args.plugin, args.case_id)
        if args.action == "show":
            show(target)
        else:
            delete(target, args.confirm_delete)
        return 0
    except StoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

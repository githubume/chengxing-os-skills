#!/usr/bin/env python3
"""Validate canonical shared references, schemas, examples, and safety invariants."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import ValidationError
except ImportError as exc:  # pragma: no cover - explicit dependency error
    raise SystemExit("validate_shared.py requires the 'jsonschema' package") from exc


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "shared"
MANIFEST = SHARED / "manifest.json"

REQUIRED_MARKDOWN = {
    "core-models/behavior-method.md": ["场景行为单元", "九个诊断镜头", "最小充分干预", "跟踪更新"],
    "safety/routing.md": ["B1", "B2", "B3", "停止普通路径", "B3 禁止项"],
    "safety/privacy-design.md": ["默认不保存", "写入流程", "儿童", "删除", "产品安全基线"],
    "evidence/evidence-policy.md": ["用户陈述", "行为假设", "证据等级", "禁止表述"],
    "quality-gates/output-quality.md": ["B1/B2", "parent-learning", "conflict-reset", "文件写入"],
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_rejected(validator: Draft202012Validator, value: dict, label: str, errors: list[str]) -> None:
    try:
        validator.validate(value)
    except ValidationError:
        return
    errors.append(f"negative schema case unexpectedly passed: {label}")


def validate() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.is_file():
        return ["shared/manifest.json missing"]
    manifest = load_json(MANIFEST)
    listed = manifest.get("files")
    if not isinstance(listed, list) or not listed or len(listed) != len(set(listed)):
        return ["manifest files must be a non-empty unique array"]
    actual = sorted(
        str(path.relative_to(SHARED))
        for path in SHARED.rglob("*")
        if path.is_file() and path != MANIFEST
    )
    if sorted(listed) != actual:
        errors.append(f"manifest mismatch: listed={sorted(listed)!r}, actual={actual!r}")
    for relative in listed:
        path = SHARED / relative
        if not path.is_file():
            errors.append(f"missing shared file: {relative}")
        if path.is_symlink():
            errors.append(f"shared file must not be symlink: {relative}")

    for relative, needles in REQUIRED_MARKDOWN.items():
        text = (SHARED / relative).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{relative}: missing required concept {needle!r}")

    profile_schema = load_json(SHARED / "profile-schema/profile.schema.json")
    case_schema = load_json(SHARED / "case-schema/case.schema.json")
    profile_validator = Draft202012Validator(profile_schema, format_checker=FormatChecker())
    case_validator = Draft202012Validator(case_schema, format_checker=FormatChecker())
    profile = load_json(SHARED / "profile-schema/example.profile.json")
    case = load_json(SHARED / "case-schema/example.case.json")
    for label, validator, value in (
        ("example profile", profile_validator, profile),
        ("example case", case_validator, case),
    ):
        try:
            validator.validate(value)
        except ValidationError as exc:
            errors.append(f"{label} invalid: {exc.message}")

    with_name = copy.deepcopy(profile)
    with_name["full_name"] = "虚构姓名"
    assert_rejected(profile_validator, with_name, "profile with full_name", errors)

    parent = copy.deepcopy(profile)
    parent["plugin"] = "parent-learning"
    assert_rejected(profile_validator, parent, "parent profile with habit domain", errors)

    four_metrics = copy.deepcopy(case)
    four_metrics["experiment"]["metrics"] = ["a", "b", "c", "d"]
    assert_rejected(case_validator, four_metrics, "case with four metrics", errors)

    unsafe_b3 = copy.deepcopy(case)
    unsafe_b3["route"] = "B3"
    unsafe_b3["safety"] = {
        "route_reason": "synthetic test",
        "ordinary_plan_stopped": False,
        "professional_review_required": False,
    }
    assert_rejected(case_validator, unsafe_b3, "B3 with ordinary experiment", errors)

    q0_with_plan = copy.deepcopy(case)
    q0_with_plan["quality_level"] = "Q0"
    assert_rejected(case_validator, q0_with_plan, "Q0 with experiment", errors)

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Shared core validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Shared core valid: manifest, 5 runtime references, 2 schemas, 2 examples, negative invariants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

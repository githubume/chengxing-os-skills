#!/usr/bin/env python3
"""Validate cross-repository release versions and fail-closed link states."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ("habit-rebuild", "parent-learning", "conflict-reset")
LINK_KEYS = (
    "website_product_page",
    "github_source",
    "feishu_guide",
    "online_use",
    "seven_day_entry",
    "day3_entry",
    "day7_entry",
)
BLOCKING_SURFACES = (
    "website_version_display",
    "feishu_guides",
    "day3_day7_forms",
    "g8_human_safety_review",
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(require_ready: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    blockers: list[str] = []
    contract = load(ROOT / "release-contract.json")
    version = contract.get("release_version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        return ["release-contract.json has an invalid release_version"], []

    surfaces = contract.get("surfaces")
    if not isinstance(surfaces, dict):
        return ["release-contract.json surfaces must be an object"], []
    for surface in BLOCKING_SURFACES:
        if surfaces.get(surface) != "ready":
            blockers.append(surface)

    public_tag = contract.get("current_public_tag")
    if not isinstance(public_tag, str) or not re.fullmatch(r"v\d+\.\d+\.\d+", public_tag):
        errors.append("current_public_tag must be a semantic version tag")
    if not (ROOT / "RELEASE.md").is_file():
        errors.append("RELEASE.md missing")

    for plugin in PLUGINS:
        plugin_root = ROOT / "plugins" / plugin
        for platform in (".claude-plugin", ".codex-plugin"):
            manifest = load(plugin_root / platform / "plugin.json")
            if manifest.get("name") != plugin:
                errors.append(f"{plugin}: {platform} name mismatch")
            if manifest.get("version") != version:
                errors.append(f"{plugin}: {platform} version must be {version}")

        links = load(plugin_root / "docs-link.json")
        if links.get("schema_version") != 1 or links.get("plugin") != plugin:
            errors.append(f"{plugin}: docs-link identity mismatch")
        if links.get("plugin_version") != version:
            errors.append(f"{plugin}: docs-link version must be {version}")
        if set(links) != {"schema_version", "plugin", "plugin_version", *LINK_KEYS}:
            errors.append(f"{plugin}: docs-link fields mismatch")
            continue

        for key in LINK_KEYS:
            entry = links[key]
            if not isinstance(entry, dict) or "status" not in entry or "url" not in entry:
                errors.append(f"{plugin}: {key} must contain status and url")
                continue
            status = entry["status"]
            url = entry["url"]
            if status == "available":
                if not isinstance(url, str) or not url.startswith("https://"):
                    errors.append(f"{plugin}: available {key} needs an HTTPS URL")
            elif status in {"blocked", "not_applicable", "local_workflow"}:
                if url is not None:
                    errors.append(f"{plugin}: {status} {key} must keep url null")
                if status in {"blocked", "not_applicable"} and not entry.get("reason"):
                    errors.append(f"{plugin}: {key} needs a reason")
                if status == "blocked":
                    blockers.append(f"{plugin}:{key}")
            else:
                errors.append(f"{plugin}: {key} has unknown status {status!r}")

        serialized = json.dumps(links, ensure_ascii=False)
        if re.search(r"(?:docx|wik|bascn|tbl)[A-Za-z0-9_-]{8,}", serialized):
            errors.append(f"{plugin}: docs-link leaks an internal Feishu token")
        if not (plugin_root / "README.md").is_file():
            errors.append(f"{plugin}: README.md missing")
        changelog = plugin_root / "CHANGELOG.md"
        if not changelog.is_file() or f"[{version}]" not in changelog.read_text(encoding="utf-8"):
            errors.append(f"{plugin}: changelog does not contain {version}")

    root_changelog = ROOT / "CHANGELOG.md"
    if not root_changelog.is_file() or f"[{version}]" not in root_changelog.read_text(encoding="utf-8"):
        errors.append(f"root changelog does not contain {version}")

    expected_state = "ready" if not blockers else "blocked"
    if contract.get("release_state") != expected_state:
        errors.append(
            f"release_state must be {expected_state!r} while blockers={sorted(set(blockers))!r}"
        )
    if require_ready and blockers:
        errors.append(f"release is blocked by: {', '.join(sorted(set(blockers)))}")
    return errors, sorted(set(blockers))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    errors, blockers = validate(require_ready=args.require_ready)
    if errors:
        print("Release contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Release contract valid: 3 plugins share one version; "
        f"release remains blocked by {len(blockers)} explicit gates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

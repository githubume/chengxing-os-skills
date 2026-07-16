#!/usr/bin/env python3
"""Validate Claude Code and Codex distribution manifests and adapters."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ("habit-rebuild", "parent-learning", "conflict-reset")
ADAPTERS = ("chengxing-habit", "chengxing-parent", "chengxing-conflict")
MARKETPLACE = "chengxing-os-skills"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    claude_market = load(ROOT / ".claude-plugin" / "marketplace.json")
    codex_market = load(ROOT / ".agents" / "plugins" / "marketplace.json")
    if claude_market.get("name") != MARKETPLACE:
        errors.append("Claude marketplace name mismatch")
    if codex_market.get("name") != MARKETPLACE:
        errors.append("Codex marketplace name mismatch")
    claude_entries = {item.get("name"): item for item in claude_market.get("plugins", [])}
    codex_entries = {item.get("name"): item for item in codex_market.get("plugins", [])}
    if tuple(claude_entries) != PLUGINS or tuple(codex_entries) != PLUGINS:
        errors.append("marketplaces must contain exactly the three plugins in stable order")
    for plugin in PLUGINS:
        expected = f"./plugins/{plugin}"
        if claude_entries.get(plugin, {}).get("source") != expected:
            errors.append(f"Claude source mismatch: {plugin}")
        source = codex_entries.get(plugin, {}).get("source", {})
        if source != {"source": "local", "path": expected}:
            errors.append(f"Codex source mismatch: {plugin}")
        policy = codex_entries.get(plugin, {}).get("policy", {})
        if policy.get("installation") != "AVAILABLE" or policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
            errors.append(f"Codex policy invalid: {plugin}")
        for platform in (".claude-plugin", ".codex-plugin"):
            manifest = ROOT / "plugins" / plugin / platform / "plugin.json"
            if not manifest.is_file() or load(manifest).get("name") != plugin:
                errors.append(f"{platform} manifest invalid: {plugin}")
    for adapter in ADAPTERS:
        path = ROOT / ".agents" / "skills" / adapter / "SKILL.md"
        if not path.is_file():
            errors.append(f"adapter missing: {adapter}")
            continue
        text = path.read_text(encoding="utf-8")
        if "chengxing-os-managed-adapter" not in text or not re.match(r"^---\n", text):
            errors.append(f"adapter metadata invalid: {adapter}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    install_guide_path = ROOT / "INSTALL.md"
    if not install_guide_path.is_file():
        errors.append("INSTALL.md missing")
        install_guide = ""
    else:
        install_guide = install_guide_path.read_text(encoding="utf-8")

    readme_commands = [
        f"claude plugin marketplace add githubume/{MARKETPLACE}",
        f"codex plugin marketplace add githubume/{MARKETPLACE}",
        "codex plugin add habit-rebuild@chengxing-os-skills",
        "codex plugin add parent-learning@chengxing-os-skills",
        "codex plugin add conflict-reset@chengxing-os-skills",
        "[完整安装指南](INSTALL.md)",
    ]
    for command in readme_commands:
        if command not in readme:
            errors.append(f"README installation command missing: {command}")

    guide_commands = [
        "claude plugin marketplace update chengxing-os-skills",
        "claude plugin uninstall habit-rebuild@chengxing-os-skills",
        "codex plugin marketplace upgrade chengxing-os-skills",
        "codex plugin remove habit-rebuild@chengxing-os-skills",
        "manage_codex_adapters.py verify",
        "manage_codex_adapters.py uninstall",
    ]
    for command in guide_commands:
        if command not in install_guide:
            errors.append(f"INSTALL.md lifecycle command missing: {command}")

    if "codex plugin install " in readme or "codex plugin install " in install_guide:
        errors.append("Codex documentation uses unsupported `plugin install`; use `plugin add`")
    if errors:
        print("Distribution validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Distribution valid: 3 Claude plugins, 3 Codex plugins, 3 compatibility adapters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

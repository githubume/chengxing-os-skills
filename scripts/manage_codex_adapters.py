#!/usr/bin/env python3
"""Install, verify, upgrade, or uninstall Chengxing OS Codex compatibility adapters."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path


ADAPTERS = ("chengxing-habit", "chengxing-parent", "chengxing-conflict")
PLUGINS = ("habit-rebuild", "parent-learning", "conflict-reset")
MARKER = "<!-- chengxing-os-managed-adapter -->"
VENDOR_MARKER = ".chengxing-os-vendor"


class InstallError(RuntimeError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def codex_root(raw: str | None) -> Path:
    if raw:
        return Path(raw).expanduser().resolve()
    if os.environ.get("CODEX_HOME"):
        return Path(os.environ["CODEX_HOME"]).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def managed_adapter(path: Path) -> bool:
    skill = path / "SKILL.md"
    return skill.is_file() and MARKER in skill.read_text(encoding="utf-8")


def managed_vendor(path: Path) -> bool:
    return (path / VENDOR_MARKER).is_file()


def stage_package(stage: Path, root: Path) -> None:
    vendor = stage / "vendor"
    vendor.mkdir(parents=True)
    (vendor / VENDOR_MARKER).write_text("chengxing-os-skills\n", encoding="utf-8")
    shutil.copy2(root / ".agents" / "plugins" / "marketplace.json", vendor / "marketplace.json")
    for plugin in PLUGINS:
        shutil.copytree(root / "plugins" / plugin, vendor / "plugins" / plugin)
    adapters = stage / "adapters"
    for adapter in ADAPTERS:
        shutil.copytree(root / ".agents" / "skills" / adapter, adapters / adapter)


def replace_managed(source: Path, target: Path, *, kind: str) -> None:
    if target.exists():
        allowed = managed_vendor(target) if kind == "vendor" else managed_adapter(target)
        if not allowed:
            raise InstallError(f"refusing to replace unmanaged {kind}: {target}")
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    source.rename(target)


def install(root: Path, codex: Path) -> dict[str, object]:
    codex.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="chengxing-install-", dir=str(codex)) as tmp:
        stage = Path(tmp)
        stage_package(stage, root)
        vendor_target = codex / "vendor" / "chengxing-os-skills"
        replace_managed(stage / "vendor", vendor_target, kind="vendor")
        installed: list[str] = []
        for adapter in ADAPTERS:
            target = codex / "skills" / adapter
            replace_managed(stage / "adapters" / adapter, target, kind="adapter")
            installed.append(str(target))
    return {
        "action": "installed",
        "vendor": str(codex / "vendor" / "chengxing-os-skills"),
        "adapters": installed,
        "user_data_preserved": str(Path.home() / ".chengxing-os"),
    }


def verify(codex: Path) -> dict[str, object]:
    vendor = codex / "vendor" / "chengxing-os-skills"
    errors: list[str] = []
    if not managed_vendor(vendor):
        errors.append(f"managed vendor missing: {vendor}")
    for plugin in PLUGINS:
        if not (vendor / "plugins" / plugin / ".codex-plugin" / "plugin.json").is_file():
            errors.append(f"plugin missing: {plugin}")
    for adapter in ADAPTERS:
        if not managed_adapter(codex / "skills" / adapter):
            errors.append(f"adapter missing or unmanaged: {adapter}")
    if errors:
        raise InstallError("; ".join(errors))
    return {"action": "verified", "codex_home": str(codex), "plugins": list(PLUGINS), "adapters": list(ADAPTERS)}


def uninstall(codex: Path) -> dict[str, object]:
    removed: list[str] = []
    for adapter in ADAPTERS:
        target = codex / "skills" / adapter
        if target.exists():
            if not managed_adapter(target):
                raise InstallError(f"refusing to remove unmanaged adapter: {target}")
            shutil.rmtree(target)
            removed.append(str(target))
    vendor = codex / "vendor" / "chengxing-os-skills"
    if vendor.exists():
        if not managed_vendor(vendor):
            raise InstallError(f"refusing to remove unmanaged vendor: {vendor}")
        shutil.rmtree(vendor)
        removed.append(str(vendor))
    return {
        "action": "uninstalled",
        "removed": removed,
        "user_data_preserved": str(Path.home() / ".chengxing-os"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("install", "upgrade", "verify", "uninstall"))
    parser.add_argument("--codex-home", help="Test or alternate Codex home; defaults to CODEX_HOME or ~/.codex")
    args = parser.parse_args()
    codex = codex_root(args.codex_home)
    try:
        if args.action in {"install", "upgrade"}:
            result = install(repo_root(), codex)
            result["action"] = "installed" if args.action == "install" else "upgraded"
        elif args.action == "verify":
            result = verify(codex)
        else:
            result = uninstall(codex)
    except InstallError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

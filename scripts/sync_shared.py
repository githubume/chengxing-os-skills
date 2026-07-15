#!/usr/bin/env python3
"""Package the canonical shared core into independently installable plugins."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "shared"
PLUGINS = ("habit-rebuild", "parent-learning", "conflict-reset")
DESTINATION_NAME = "chengxing-shared"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def destination(plugin_root: Path) -> Path:
    resolved_root = plugin_root.resolve()
    target = (resolved_root / "references" / DESTINATION_NAME).resolve()
    if target.parent.parent != resolved_root or target.name != DESTINATION_NAME:
        raise ValueError(f"unsafe destination: {target}")
    return target


def sync_one(plugin_root: Path) -> None:
    if not plugin_root.is_dir():
        raise FileNotFoundError(f"plugin directory missing: {plugin_root}")
    target = destination(plugin_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.parent / f".{DESTINATION_NAME}.tmp-{os.getpid()}"
    if temporary.exists():
        shutil.rmtree(temporary)
    shutil.copytree(SOURCE, temporary, symlinks=False)
    if target.exists():
        shutil.rmtree(target)
    temporary.replace(target)


def check_one(plugin_root: Path) -> list[str]:
    target = destination(plugin_root)
    if not target.is_dir():
        return [f"missing packaged shared core: {target}"]
    source_files = files(SOURCE)
    target_files = files(target)
    if source_files != target_files:
        missing = sorted(set(source_files) - set(target_files))
        extra = sorted(set(target_files) - set(source_files))
        changed = sorted(
            key for key in set(source_files) & set(target_files)
            if source_files[key] != target_files[key]
        )
        return [f"{plugin_root.name}: shared mismatch missing={missing}, extra={extra}, changed={changed}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-root", type=Path, default=ROOT / "plugins")
    parser.add_argument("--plugin", action="append", choices=PLUGINS, dest="plugins", help="Limit sync/check to one or more plugins; defaults to all three.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not SOURCE.is_dir() or not (SOURCE / "manifest.json").is_file():
        print("canonical shared source missing", file=sys.stderr)
        return 1
    selected = tuple(args.plugins) if args.plugins else PLUGINS
    roots = [args.target_root / name for name in selected]
    if args.dry_run:
        for root in roots:
            print(destination(root))
        return 0
    if args.check:
        errors = [error for root in roots for error in check_one(root)]
        if errors:
            print("Packaged shared core check failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print(f"Packaged shared core matches canonical source for {len(roots)} plugin(s).")
        return 0
    for root in roots:
        sync_one(root)
    print(f"Packaged canonical shared core into {len(roots)} plugin(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

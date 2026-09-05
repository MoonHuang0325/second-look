#!/usr/bin/env python3
"""Install or explicitly upgrade Second Look, keeping a recoverable backup."""

import argparse
import json
import re
import shutil
import tempfile
import uuid
from pathlib import Path


def install(source, parent, upgrade=False):
    source, parent = Path(source).resolve(), Path(parent).expanduser().resolve()
    if not (source / "SKILL.md").is_file():
        raise ValueError("Skill source is missing")
    if any(p.is_symlink() for p in source.rglob("*")):
        raise ValueError("Refusing symlinks in skill source")
    target = parent / "second-look"
    if source == target or target in source.parents or source in target.parents:
        raise ValueError("Source and installation must be separate directories")
    if target.is_symlink():
        raise ValueError("This installation is a symlink; update it with its original installer")
    exists = target.exists()
    if exists:
        if not upgrade:
            raise ValueError("Existing installation left unchanged: " + str(target))
        marker = target / "SKILL.md"
        if not marker.is_file() or not re.search(r"^name: second-look$", marker.read_text(encoding="utf-8"), re.M):
            raise ValueError("Refusing to replace a directory without the Second Look identity")
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".second-look-install-", dir=str(parent)))
    backup = None
    try:
        shutil.copytree(source, staging / "second-look", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        license_path = source.parents[1] / "LICENSE"
        if license_path.is_file():
            shutil.copy2(license_path, staging / "second-look/LICENSE")
        if exists:
            # Backup is outside the discoverable skills directory, so its SKILL.md cannot
            # become a second active copy. User additions stay in this recoverable copy.
            backup_root = parent.parent / "second-look-backups"
            backup_root.mkdir(parents=True, exist_ok=True)
            backup = backup_root / uuid.uuid4().hex
            target.rename(backup)
        try:
            (staging / "second-look").rename(target)
        except OSError:
            if backup is not None:
                backup.rename(target)
            raise
    finally:
        shutil.rmtree(staging)
    return target, backup


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", choices=("codex", "claude"), required=True)
    p.add_argument("--dest", help="Override skill parent directory")
    p.add_argument("--upgrade", action="store_true", help="Back up an existing Second Look installation before replacing it")
    args = p.parse_args()
    parent = args.dest or str(Path.home() / (".agents/skills" if args.target == "codex" else ".claude/skills"))
    try:
        target, backup = install(Path(__file__).resolve().parents[1] / "skills/second-look", parent, args.upgrade)
        print(json.dumps({"installed": str(target), "target": args.target, "backup": str(backup) if backup else None,
                          "private_ledger_modified": False, "next_step": "Start a new agent session and invoke Second Look."}))
    except (ValueError, OSError) as exc:
        p.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()

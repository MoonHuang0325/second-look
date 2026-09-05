#!/usr/bin/env python3
"""Install the standard skill locally. Existing installs are never overwritten."""

import argparse
import json
import shutil
import tempfile
from pathlib import Path


def install(source, parent):
    source, parent = Path(source).resolve(), Path(parent).expanduser().resolve()
    if not (source / "SKILL.md").is_file():
        raise ValueError("Skill source is missing")
    if any(p.is_symlink() for p in source.rglob("*")):
        raise ValueError("Refusing symlinks in skill source")
    target = parent / "second-look"
    if target.exists() or target.is_symlink():
        raise ValueError("Existing installation left unchanged: " + str(target))
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".second-look-install-", dir=str(parent)))
    try:
        shutil.copytree(source, staging / "second-look", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        license_path = source.parents[1] / "LICENSE"
        if license_path.is_file():
            shutil.copy2(license_path, staging / "second-look/LICENSE")
        (staging / "second-look").rename(target)
    finally:
        shutil.rmtree(staging)
    return target


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", choices=("codex", "claude"), required=True)
    p.add_argument("--dest", help="Override skill parent directory, useful for sandboxed installs")
    args = p.parse_args()
    parent = args.dest or str(Path.home() / (".agents/skills" if args.target == "codex" else ".claude/skills"))
    try:
        target = install(Path(__file__).resolve().parents[1] / "skills/second-look", parent)
        print(json.dumps({"installed": str(target), "target": args.target, "overwrote_existing": False}))
    except (ValueError, OSError) as exc:
        p.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()

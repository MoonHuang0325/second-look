#!/usr/bin/env python3
"""Reproducible, allowlisted archives. Never package user data or evaluation runs."""

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/second-look"


def files():
    paths = [SKILL / "SKILL.md", SKILL / "agents/openai.yaml"]
    for directory, suffix in (("references", ".md"), ("scripts", ".py")):
        paths.extend(sorted((SKILL / directory).rglob("*" + suffix)))
    for path in paths:
        if path.is_symlink() or SKILL not in path.resolve().parents or not path.is_file():
            raise ValueError("Unsafe/missing package member: " + str(path))
    return paths


def archive(output, members):
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, content in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, content)


def build(output=None):
    output = Path(output or ROOT / "dist")
    output.mkdir(parents=True, exist_ok=True)
    version = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    standard = {"second-look/" + p.relative_to(SKILL).as_posix(): p.read_bytes() for p in files()}
    standard["second-look/LICENSE"] = (ROOT / "LICENSE").read_bytes()
    plugin = {"second-look/skills/second-look/" + p.relative_to(SKILL).as_posix(): p.read_bytes() for p in files()}
    for name in (".codex-plugin/plugin.json", ".second-look-public", "LICENSE", "README.md", "README.zh-CN.md", "CONTRIBUTING.md", "evals/README.md", "evals/pilot.md"):
        plugin["second-look/" + name] = (ROOT / name).read_bytes()
    # Docs are part of the installation instructions linked from the README.
    for p in sorted((ROOT / "docs").glob("*.md")):
        plugin["second-look/docs/" + p.name] = p.read_bytes()
    for p in sorted((ROOT / "examples").rglob("*.md")):
        plugin["second-look/" + p.relative_to(ROOT).as_posix()] = p.read_bytes()
    for name in ("install.py", "build.py"):
        plugin["second-look/tools/" + name] = (ROOT / "tools" / name).read_bytes()
    archives = {}
    for kind, members in (("skill", standard), ("openai-plugin", plugin)):
        path = output / ("second-look-" + version + "-" + kind + ".zip")
        archive(path, members)
        archives[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text("".join(h + "  " + name + "\n" for name, h in sorted(archives.items())))
    return archives


if __name__ == "__main__":
    print(json.dumps(build(sys.argv[1] if len(sys.argv) > 1 else None), indent=2))

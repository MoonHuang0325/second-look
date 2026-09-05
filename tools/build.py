#!/usr/bin/env python3
"""Reproducible, allowlisted archives. Never package user data or evaluation runs."""

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/second-look"


def files():
    paths = [SKILL / "SKILL.md", SKILL / "agents/openai.yaml", SKILL / "assets/demo/START.md", SKILL / "assets/demo/history.md"]
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
    for name in (".codex-plugin/plugin.json", ".second-look-public", "LICENSE", "README.md", "README.zh-CN.md", "CONTRIBUTING.md", "CHANGELOG.md", "evals/README.md", "evals/pilot.md"):
        plugin["second-look/" + name] = (ROOT / name).read_bytes()
    # Docs are part of the installation instructions linked from the README.
    for p in sorted((ROOT / "docs").glob("*.md")):
        plugin["second-look/docs/" + p.name] = p.read_bytes()
    for p in sorted((ROOT / "examples").rglob("*.md")):
        plugin["second-look/" + p.relative_to(ROOT).as_posix()] = p.read_bytes()
    for directory, suffixes in (("assets", {".png", ".svg"}), ("docs/launch", {".md", ".csv"}),
                                ("evals/observations", {".md", ".py", ".txt"})):
        for p in sorted((ROOT / directory).rglob("*")):
            if p.suffix in suffixes and "__pycache__" not in p.parts:
                if p.is_symlink() or ROOT not in p.resolve().parents:
                    raise ValueError("Unsafe public resource: " + str(p))
                plugin["second-look/" + p.relative_to(ROOT).as_posix()] = p.read_bytes()
    # Launch files stand alone: resolve links outside the kit to the public source.
    launch = {"second-look-launch/LICENSE": (ROOT / "LICENSE").read_bytes()}
    for name, content in plugin.items():
        relative = name.removeprefix("second-look/") if hasattr(str, "removeprefix") else name[len("second-look/"):]
        if relative.startswith(("docs/launch/", "assets/")):
            if relative.endswith(".md"):
                def portable_link(match):
                    url = match.group(1)
                    if re.match(r"^[a-z]+://", url) or url.startswith("#"):
                        return match.group(0)
                    target, _, anchor = url.partition("#")
                    resolved = (ROOT / relative).parent.joinpath(target).resolve().relative_to(ROOT).as_posix()
                    if resolved.startswith(("docs/launch/", "assets/")):
                        return match.group(0)
                    return "](https://github.com/MoonHuang0325/second-look/blob/main/" + resolved + ("#" + anchor if anchor else "") + ")"
                content = re.sub(r"\]\(([^)]+)\)", portable_link, content.decode("utf-8")).encode("utf-8")
            launch["second-look-launch/" + relative] = content
    launch["second-look-launch/START.md"] = b"# Launch kit\n\nStart with [the action manual](docs/launch/action-manual.zh-CN.md). All copy is a draft; nothing has been posted automatically.\n"
    for name in ("install.py", "build.py"):
        plugin["second-look/tools/" + name] = (ROOT / "tools" / name).read_bytes()
    archives = {}
    for kind, members in (("skill", standard), ("openai-plugin", plugin), ("launch-kit", launch)):
        path = output / ("second-look-" + version + "-" + kind + ".zip")
        archive(path, members)
        archives[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text("".join(h + "  " + name + "\n" for name, h in sorted(archives.items())))
    return archives


if __name__ == "__main__":
    print(json.dumps(build(sys.argv[1] if len(sys.argv) > 1 else None), indent=2))

#!/usr/bin/env python3
"""Offline, standard-library structural validation. Not a model efficacy test."""

import ast
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate():
    errors = []
    skill = ROOT / "skills/second-look/SKILL.md"
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        errors.append("Missing skill frontmatter")
    else:
        frontmatter = text.split("---", 2)[1]
        keys = re.findall(r"^(\w+):", frontmatter, flags=re.M)
        if set(keys) - {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}:
            errors.append("Nonportable frontmatter")
        if not re.search(r"^name: second-look$", frontmatter, re.M):
            errors.append("Skill name must match directory")
        if not re.search(r"^description: .{25,1024}$", frontmatter, re.M):
            errors.append("Missing or overly long description")
    if len(text.splitlines()) >= 500:
        errors.append("Skill exceeds progressive-disclosure limit")
    for file in ROOT.rglob("*.py"):
        if not any(p in ("dist", ".git", "__pycache__") for p in file.parts):
            ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
    for file in (ROOT / "skills").rglob("*.md"):
        if "[TODO:" in file.read_text(encoding="utf-8"):
            errors.append("Unfinished scaffold: " + str(file))
    for file in ROOT.rglob("*.md"):
        if "dist" in file.parts:
            continue
        for link in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            if re.match(r"^[a-z]+://", link) or link.startswith("#"):
                continue
            target = link.split("#")[0]
            if target and not (file.parent / target).exists():
                errors.append("Broken relative link: " + str(file.relative_to(ROOT)) + " -> " + link)
    manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if manifest.get("name") != "second-look" or manifest.get("license") != "MIT":
        errors.append("Invalid plugin identity/license")
    if manifest.get("skills") != "./skills/":
        errors.append("Plugin must use canonical skills directory")
    for prohibited in ("hooks", "apps", "mcpServers"):
        if prohibited in manifest:
            errors.append("Unexpected service or hook: " + prohibited)
    all_cases = []
    for split, count in (("development", 16), ("holdout", 8)):
        cases = json.loads((ROOT / "evals" / split / "cases.json").read_text(encoding="utf-8"))
        if len(cases) != count:
            errors.append("Wrong case count: " + split)
        for case in cases:
            if case["split"] != split or not case["synthetic"] or not case["expected"]["rubric"] or not case["history"]:
                errors.append("Incomplete case: " + case["id"])
        all_cases.extend(cases)
    if len({c["id"] for c in all_cases}) != 24:
        errors.append("Case IDs must be unique")
    if Counter(c["audience"] for c in all_cases) != {"knowledge": 12, "developer": 12}:
        errors.append("Audience coverage is unbalanced")
    if errors:
        raise ValueError("\n".join(errors))
    return {"skill_lines": len(text.splitlines()), "behavioral_cases": len(all_cases), "status": "structure_valid",
            "behavioral_efficacy": "not established by structural validation"}


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))

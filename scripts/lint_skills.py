#!/usr/bin/env python3
"""Lint every SKILL.md: the YAML frontmatter must parse and carry ``name`` and
``description``, and ``name`` must equal the skill's directory (document-skill,
"Entrypoint").

An unquoted ``: `` inside a plain-scalar description is the usual failure: YAML
reads it as a mapping indicator, the frontmatter does not parse, and the skill
renders as a bare ``SKILL`` in the session catalog (sucoder-skills #1).  Use a
folded block (``description: >-``) or quote the scalar.

Usage: python3 scripts/lint_skills.py [ROOT]   (default: the repo root)
Exit status is the number of failing files.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("lint_skills.py needs PyYAML (pip install pyyaml)")

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def lint(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER.match(text)
    if not m:
        return ["no YAML frontmatter (file must start with a --- block)"]
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        msg = str(exc).splitlines()[0]
        hint = ""
        for line in m.group(1).splitlines():
            if line.startswith("description:") and ": " in line.split(":", 1)[1]:
                hint = " -- unquoted ': ' inside the description; fold it with 'description: >-'"
        return [f"frontmatter does not parse: {msg}{hint}"]
    problems = []
    if not isinstance(meta, dict):
        return ["frontmatter is not a mapping"]
    for key in ("name", "description"):
        if not isinstance(meta.get(key), str) or not meta[key].strip():
            problems.append(f"missing or empty '{key}'")
    if isinstance(meta.get("name"), str) and meta["name"] != path.parent.name:
        problems.append(f"name {meta['name']!r} != directory {path.parent.name!r}")
    return problems


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    files = sorted(root.rglob("SKILL.md"))
    failures = 0
    for path in files:
        for problem in lint(path):
            failures += 1
            print(f"{path.relative_to(root)}: {problem}")
    print(f"{len(files)} SKILL.md checked, {failures} problem(s)")
    return failures


if __name__ == "__main__":
    sys.exit(main(sys.argv))

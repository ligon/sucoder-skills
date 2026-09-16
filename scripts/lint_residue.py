#!/usr/bin/env python3
"""Check the agent-residue catalog against the two skills that restate it.

The residue phenomena are enumerated canonically in
``ligon-voice/references/agent-residue.org`` (one ``** =id=`` heading each).
Both halves of the writer/editor loop keep their own short operational list
inline, keyed to those ids, because each needs the rules at load time without a
second file read: the writer to avoid producing the residue, the editor to hunt
it.  Three copies of one list is a drift hazard, so this lints the invariant:

  the id set in the catalog == the id set in research-writer/SKILL.md
                            == the id set in technical-editor/SKILL.md

Each SKILL.md declares its ids as description-list bullets, ``- =some-id= ::``.
Adding or renaming a phenomenon means touching all three files; this says so
instead of letting the lists rot apart.

Usage: python3 scripts/lint_residue.py [ROOT]   (default: the repo root)
Exit status is the number of problems found.
"""
import re
import sys
from pathlib import Path

CATALOG = Path("ligon-voice/references/agent-residue.org")
CONSUMERS = (Path("research-writer/SKILL.md"), Path("technical-editor/SKILL.md"))

CATALOG_ID = re.compile(r"^\*\* =([a-z][a-z-]*)=\s*$", re.M)
CONSUMER_ID = re.compile(r"^- =([a-z][a-z-]*)= ::", re.M)


def ids(path: Path, pattern: re.Pattern) -> list[str]:
    return pattern.findall(path.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    problems = []

    catalog = root / CATALOG
    if not catalog.exists():
        print(f"{CATALOG}: missing (the canonical residue catalog)")
        return 1

    canonical = ids(catalog, CATALOG_ID)
    if not canonical:
        problems.append(f"{CATALOG}: no '** =id=' headings found")
    duplicates = {i for i in canonical if canonical.count(i) > 1}
    for dup in sorted(duplicates):
        problems.append(f"{CATALOG}: duplicate id {dup!r}")
    expected = set(canonical)

    for rel in CONSUMERS:
        path = root / rel
        if not path.exists():
            problems.append(f"{rel}: missing")
            continue
        found = set(ids(path, CONSUMER_ID))
        for missing in sorted(expected - found):
            problems.append(f"{rel}: missing residue id {missing!r} (in {CATALOG})")
        for extra in sorted(found - expected):
            problems.append(f"{rel}: residue id {extra!r} not in {CATALOG}")
        if CATALOG.name not in path.read_text(encoding="utf-8"):
            problems.append(f"{rel}: no pointer to {CATALOG.name}")

    for problem in problems:
        print(problem)
    print(f"{len(expected)} residue id(s) checked across {len(CONSUMERS) + 1} files, "
          f"{len(problems)} problem(s)")
    return len(problems)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

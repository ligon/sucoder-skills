#!/usr/bin/env python3
"""Build a provenance-and-quality test from passages of DISTINCT content.

The matched design in blind_compare.py shows three versions of one passage
side by side.  That is right for judging quality and wrong for judging
provenance: seeing three versions of the same content tells the reader that
exactly one of them is the human original, which is most of the answer.

Here each item is a different passage, so nothing is repeated and no item
implies anything about any other.  One arm is drawn per topic for the
generated items, and the human items come from unrelated passages.  The
grader marks provenance and quality; the key is written separately.

Usage:
  python3 scripts/blind_test.py --item human=PATH --item raw=PATH ... \\
      --out calibration/out/test.org --key calibration/out/test_key.json
"""
import argparse
import json
import random
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--item", action="append", required=True, metavar="ARM=PATH",
                    help="repeatable; the arm label and the passage file")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--key", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=20260915)
    args = ap.parse_args()

    items = []
    for spec in args.item:
        arm, _, path = spec.partition("=")
        items.append({"arm": arm, "path": Path(path)})

    random.Random(args.seed).shuffle(items)

    key, body = {}, []
    body.append("#+TITLE: Provenance and quality test\n#+OPTIONS: toc:nil\n\n")
    body.append("Each passage below is a different piece of writing; none is a\n"
                "rewrite of any other, and the mix of sources is not disclosed.\n"
                "For each, record:\n\n"
                "- guess :: who wrote it --- you, or an agent\n"
                "- quality :: 1 (bad) to 5 (publishable as is)\n"
                "- tell :: what decided it, in a line\n\n"
                "The key is held separately.  Do not open it until every item\n"
                "is graded, and resist going back to revise earlier answers\n"
                "once a later item makes the pattern feel obvious.\n\n")

    for n, item in enumerate(items, 1):
        label = f"{n:02d}"
        key[label] = {"arm": item["arm"], "source": str(item["path"])}
        text = item["path"].read_text(encoding="utf-8").strip()
        body.append(f"* Passage {label}\n\n#+begin_quote\n{text}\n#+end_quote\n\n")
        body.append("- guess :: \n- quality :: \n- tell :: \n\n")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(body), encoding="utf-8")
    args.key.write_text(json.dumps({"seed": args.seed, "key": key}, indent=1),
                        encoding="utf-8")
    counts: dict[str, int] = {}
    for item in items:
        counts[item["arm"]] = counts.get(item["arm"], 0) + 1
    print(f"{len(items)} items -> {args.out}")
    print(f"key -> {args.key}   (composition withheld from the test file)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

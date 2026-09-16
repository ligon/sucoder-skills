#!/usr/bin/env python3
"""Build a blinded reading set from matched passages.

The detector answers "was this machine-written." It cannot answer "is this any
good," and the interesting case is precisely where the two disagree: prose that
reads as human to a classifier and badly to an editor. That judgment needs a
human, and it needs to be blind, because knowing which arm a passage came from
is enough to produce the expected ranking.

Input: a directory per arm, with matching filenames across arms (the same brief
written three ways). Output: an Org file presenting each matched set with the
arms shuffled and labelled A/B/C, plus a key file written separately.

Do not open the key until the ranking is recorded.

Usage:
  python3 scripts/blind_compare.py --arm human=DIR --arm raw=DIR --arm skill=DIR \\
      --out calibration/out/blind.org --key calibration/out/blind_key.json
"""
import argparse
import json
import random
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", required=True,
                    metavar="NAME=DIR", help="repeatable, e.g. --arm human=path/")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--key", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=20260915,
                    help="recorded so the blinding is reproducible")
    args = ap.parse_args()

    arms = {}
    for spec in args.arm:
        name, _, directory = spec.partition("=")
        arms[name] = Path(directory)

    stems = None
    for name, directory in arms.items():
        found = {p.stem for p in directory.glob("*.txt")}
        stems = found if stems is None else (stems & found)
    stems = sorted(stems or [])
    if not stems:
        raise SystemExit("no filenames common to every arm; nothing to compare")

    rng = random.Random(args.seed)
    key, body = {}, []
    body.append("#+TITLE: Blinded passage comparison\n")
    body.append("#+OPTIONS: toc:nil\n\n")
    body.append("Each set below is the same content written three ways.  Rank\n"
                "A/B/C within each set, best prose first, and note what is wrong\n"
                "with the weakest.  The arms are shuffled per set and the key is\n"
                "held separately; do not read it before recording a ranking.\n\n")

    for n, stem in enumerate(stems, 1):
        order = list(arms)
        rng.shuffle(order)
        key[stem] = {label: arm for label, arm in zip("ABC", order)}
        body.append(f"* Set {n} ({stem})\n")
        for label, arm in zip("ABC", order):
            text = (arms[arm] / f"{stem}.txt").read_text(encoding="utf-8").strip()
            body.append(f"\n** {label}\n\n#+begin_quote\n{text}\n#+end_quote\n")
        body.append("\n** Ranking\n\n- best  :: \n- middle :: \n- worst :: \n"
                    "- what is wrong with the worst :: \n")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(body), encoding="utf-8")
    args.key.write_text(json.dumps({"seed": args.seed, "key": key}, indent=1),
                        encoding="utf-8")
    print(f"{len(stems)} matched set(s) -> {args.out}")
    print(f"key (do not open yet) -> {args.key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

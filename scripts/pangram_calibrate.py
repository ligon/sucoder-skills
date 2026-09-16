#!/usr/bin/env python3
"""Phase 0 calibration: does an AI-text detector measure anything useful about
academic economics prose?

This scores arms of text against the Pangram API and reports the distribution
per arm.  It is a measurement instrument for the writing skills, NOT a gate on
any particular draft.  The question it answers is:

  arm 'human'  --- confidently human, pre-LLM Ligon prose.  If this arm gets
                   flagged, the detector reads disciplined academic register as
                   machine-like and the whole programme stops here.
  arm 'raw'    --- model output with no skills loaded.  If this arm does not
                   separate from 'human', there is no signal to chase.
  arm 'skill'  --- current skill-assisted output.  Where we actually sit.

Only if 'human' passes and 'raw' separates is there a gradient worth using ---
and even then, use it offline to locate nameable prose faults for
ligon-voice/references/agent-residue.org.  Do not put the score in the drafting
loop: optimizing prose against a detector optimizes for evading the detector.

CONFIDENTIALITY.  This sends text to a third party.  Referee reports are
confidential by journal policy, and unpublished coauthored work is not any one
author's to upload.  Two controls, both deliberate:
  * Nothing is submitted unless it is listed by path in the manifest.
  * Paths and contents are scanned for sensitive markers and refused by
    default; an override must name the individual file.
Dry-run is the default.  You must pass --submit to spend an API call.

Usage:
  python3 scripts/pangram_calibrate.py --manifest calibration/manifest.json
  python3 scripts/pangram_calibrate.py --manifest ... --submit
  python3 scripts/pangram_calibrate.py --probe          # verify API schema
  python3 scripts/pangram_calibrate.py --report         # summarize cache only

The key is read from $PANGRAM_API_KEY, else --key-file (default
~/Downloads/pangram_api_key).  It is never written to the cache or the report.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "https://text.external-api.pangram.com"
# Pangram enforces a 50-word minimum (it needs the context to predict at all).
# Well above that, accuracy still improves with length, so 300 is the point
# below which we treat a result as weak rather than merely noisy.
PANGRAM_MIN_WORDS = 50
ADVISORY_MIN_WORDS = 300
# Billing is per word ($0.05 / 100 words), so submitting a whole document to
# ask about one paragraph is money spent on words you were not asking about.
USD_PER_WORD = 0.05 / 100

def _default_log() -> Path:
    """Where the running check log lives.

    Its value comes from being ONE file --- across every project, and across
    every account that runs a check.  A path relative to the working directory
    would give a separate log per repo, and would drop prose excerpts inside
    research repos whose .gitignore knows nothing about it.  Keying it to
    Path.home() would instead fragment it by whoever happens to be running:
    sessions run under the shared agent account, but a human may run the same
    check directly.  So prefer the agent account's home when that account
    exists, and fall back to the caller's home when it does not.
    """
    override = os.environ.get("PANGRAM_CHECK_LOG")
    if override:
        return Path(override)
    home = Path.home()
    try:
        import pwd
        home = Path(pwd.getpwnam("coder").pw_dir)
    except (ImportError, KeyError):
        pass                      # no such account, or not a POSIX system
    return home / ".sucoder" / "pangram" / "check_log.jsonl"


DEFAULT_LOG = _default_log()
DEFAULT_MODEL = "pangram-4"


def _default_key_file() -> Path:
    """Where the API key sits --- the opposite resolution from the log.

    The key is a credential the HUMAN obtained, and it lands in the human
    account's Downloads.  Path.home() resolves to whichever account is
    running, which on an agent session is the one account the key is NOT in.
    So read human_user from the sucoder config and prefer that account's
    home, falling back to the caller's.  Best-effort: any failure to read the
    config just means falling back.
    """
    bases, home = [], Path.home()
    try:
        import pwd
        import yaml
        cfg = yaml.safe_load((home / ".sucoder" / "config.yaml").read_text())
        if isinstance(cfg, dict) and cfg.get("human_user"):
            bases.append(Path(pwd.getpwnam(cfg["human_user"]).pw_dir))
    except Exception:
        pass
    bases.append(home)
    # Preferred locations first.  A credential belongs in a restricted dotdir,
    # not in Downloads --- on this workspace Downloads is a 9p mount shared
    # with the host OS, where Unix modes are not reliably enforced and the key
    # is readable by every local account.  The Downloads paths stay in the list
    # so an existing setup keeps working, but moving the key to
    # <home>/.sucoder/pangram/api_key requires no flag and no config change.
    relative = (Path(".sucoder") / "pangram" / "config.yaml",
                Path(".sucoder") / "pangram" / "api_key",
                Path("Downloads") / "pangram_api_key")
    for rel in relative:
        for base in bases:
            candidate = base / rel
            if candidate.exists():
                return candidate
    return bases[0] / relative[0]


DEFAULT_KEY_FILE = _default_key_file()

# Refused by default.  Content markers, matched against the first 4k.
SENSITIVE = re.compile(
    r"referee\s+report|report\s+on\s+the\s+paper|confidential|do\s+not\s+circulate"
    r"|letter\s+of\s+recommendation|recommendation\s+letter|tenure\s+(case|review)"
    r"|personnel|under\s+embargo|\bnda\b|salary|decision\s+letter"
    r"|should\s+not\s+be\s+made\s+part\s+of\s+the\s+case",
    re.I,
)

# Refused by default on PATH alone.  Content markers are not enough: a referee
# report at Admin/Referee/REStud/Kinnan14/report.org need not contain the words
# "referee report" anywhere, and the directory is the only reliable signal.
# These directory names are how this workspace stores other people's
# confidential material --- reports on submissions, letters about named
# individuals, tenure and search files, student records, credentials.
SENSITIVE_PATH = re.compile(
    r"(^|/)(Referee|Referees|Letters|Adhoc|AdHoc|Editorial|Students|Credentials"
    r"|GSRs|Search|Personnel|Tenure|Promotion)(/|$)"
    r"|(^|/)Employment/Review(/|$)"
    r"|(^|/)Correspondence/referee(/|$)",
    re.I,
)


# --------------------------------------------------------------------------
# Org -> prose
#
# Emacs is the parser of record.  It knows Org's grammar, so blocks, drawers,
# tables, links, footnotes and markup come out right; a pile of regexes gets
# them right only until the next edge case, and these files are old enough to
# have plenty (legacy $...$ math, #+LATEX: lines, natbib macros).  We export to
# ASCII and then tidy the residue that export deliberately leaves verbatim.
# The regex path below remains the fallback for .tex/.txt and for machines
# with no Emacs.
# --------------------------------------------------------------------------
EMACS_EXPORT = """(progn
  (require 'org) (require 'ox-ascii)
  (setq org-export-use-babel nil
        org-export-with-toc nil org-export-with-author nil
        org-export-with-title nil org-export-with-tags nil
        org-export-with-todo-keywords nil org-export-with-properties nil
        org-export-with-drawers nil org-export-with-timestamps nil
        org-export-with-latex 'verbatim
        org-ascii-text-width 72 org-ascii-headline-spacing '(1 . 1))
  (find-file %s)
  (org-ascii-export-to-ascii))"""


def emacs_export(path: Path, timeout: int = 180) -> str | None:
    """Export one Org file to ASCII via Emacs; None if that is not possible.

    org-export-use-babel is nil so that exporting a file full of source blocks
    cannot execute any of them.
    """
    if not shutil.which("emacs"):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "doc.org"
        copy.write_text(path.read_text(encoding="utf-8", errors="replace"),
                        encoding="utf-8")
        try:
            subprocess.run(["emacs", "--batch", "--eval",
                            EMACS_EXPORT % json.dumps(str(copy))],
                           capture_output=True, timeout=timeout, check=True)
        except (subprocess.SubprocessError, OSError):
            return None
        out = copy.with_suffix(".txt")
        if not out.exists():
            return None
        return out.read_text(encoding="utf-8", errors="replace")


def strip_export_furniture(text: str) -> str:
    """Drop the table of contents, headlines, and the References section.

    A file-local ``#+OPTIONS: toc:t`` outranks anything we set at export time,
    so the contents table has to come out here instead.
    """
    lines, out, i, dropping = text.splitlines(), [], 0, False
    while i < len(lines):
        line = lines[i]
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if line.strip() and re.fullmatch(r"[=~-]{3,}", nxt.strip() or "x"):
            dropping = bool(re.match(r"^\d*\.?\s*(References|Bibliography)\s*$",
                                     line.strip(), re.I))
            i += 2                                   # headline and its underline
            continue
        if re.match(r"^\s*Table of Contents\s*$", line, re.I):
            dropping = True
        if dropping and i and not line.strip() and not lines[i - 1].strip():
            dropping = False
        if not dropping:
            out.append(line)
        i += 1
    text = "\n".join(out)
    text = re.sub(r"^\s*\d+\.? +[A-Z][^.\n]{5,90}$", "", text, flags=re.M)
    return re.sub(r"^\s*_{3,}\s*$", "", text, flags=re.M)


def tidy_math(text: str, keep_math_content: bool = True) -> str:
    """Clean the math and citation residue that ASCII export leaves verbatim."""
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
    text = re.sub(r"^\s*\\begin\{(\w+\*?)\}.*?\\end\{\1\}", " ", text,
                  flags=re.M | re.S)
    text = re.sub(r"\\(cite[a-zA-Z]*|ref|eqref|label|autoref|pageref|index"
                  r"|title|author|date|thanks|documentclass|usepackage|input"
                  r"|include|bibliography|bibliographystyle|newcommand"
                  r"|renewcommand|setlength|hypersetup)"
                  r"\s*(\[[^\]]*\])?\s*\{[^}]*\}", " ", text)
    text = re.sub(r"\\(maketitle|today|newpage|clearpage|tableofcontents)\b",
                  " ", text)
    if keep_math_content:
        text = re.sub(r"\\\((.*?)\\\)", lambda m: m.group(1), text, flags=re.S)
        text = re.sub(r"\$([^$\n]{1,120})\$", r"\1", text)
        # Keep the symbol NAME, not just the backslash: \theta -> theta.  These
        # files are dense with inline math and deleting macros outright leaves
        # unreadable stubs, which is not what a reader of the paper sees.
        text = re.sub(r"\\([a-zA-Z]+)\s?", r"\1 ", text)
        text = re.sub(r"[{}^]", "", text)
    else:
        text = re.sub(r"\\\(.*?\\\)", " ", text, flags=re.S)
        text = re.sub(r"\$[^$\n]{1,120}\$", " ", text)
    text = re.sub(r"^ +", "", text, flags=re.M)
    # Stripping citations and math orphans the space before punctuation ("the
    # model ."). Left in, that is an artifact of THIS script which the
    # generated arms would not carry, so it would confound the comparison.
    text = re.sub(r"[ \t]*\n?[ \t]*([.,;:!?)])", r"\1", text)
    text = re.sub(r"([(])[ \t]*", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def org_to_prose(text: str, keep_math_content: bool = True) -> str:
    """Regex fallback for .tex/.txt, and for machines with no Emacs.

    Strips Org scaffolding structurally, then hands off to tidy_math.  It is
    deliberately the second choice: it handles the common cases and will miss
    edge cases that Emacs gets right by construction.
    """
    text = re.sub(r"^\*{15}\s.*?^\*{15}\s+END\s*$", "", text, flags=re.M | re.S)
    text = re.sub(r"^#\+\w[^\n]*\n?", "", text, flags=re.M)
    text = re.sub(r"^\s*:[A-Z_]+:\s*$.*?^\s*:END:\s*$", "", text, flags=re.M | re.S)
    text = re.sub(r"^\s*#\+begin_(\w+).*?^\s*#\+end_\1\s*$", "", text,
                  flags=re.M | re.S | re.I)
    text = re.sub(r"^\s*#[^+\n].*$", "", text, flags=re.M)      # comments
    text = re.sub(r"^\s*\|.*$", "", text, flags=re.M)           # tables
    text = re.sub(r"^\s*\[fn:[^\]]+\].*$", "", text, flags=re.M)
    text = re.sub(r"\\(begin|end)\{document\}|\\maketitle", " ", text)
    text = re.sub(r"\[\[[^\]]*?\]\[([^\]]*?)\]\]", r"\1", text)   # links
    text = re.sub(r"\[\[([^\]]*?)\]\]", " ", text)
    text = re.sub(r"\[cite[^\]]*\]", " ", text)
    text = re.sub(r"^\*+\s+.*$", "", text, flags=re.M)          # headlines
    text = re.sub(r"[=~]{1}(\S[^=~\n]*?\S)[=~]{1}", r"\1", text)
    return tidy_math(text, keep_math_content)


def to_prose(path: Path, raw: str, keep_math: bool = True,
             use_emacs: bool = True) -> tuple[str, str]:
    """Return (prose, method) for one source file."""
    if use_emacs and path.suffix in (".org", ".org_archive"):
        exported = emacs_export(path)
        if exported is not None:
            return tidy_math(strip_export_furniture(exported), keep_math), "emacs"
    return org_to_prose(raw, keep_math), "regex"


def chunk(prose: str, min_words: int, max_words: int) -> list[str]:
    """Group paragraphs into submissions of at least min_words.

    Detector accuracy degrades on short passages, so we never submit a stub;
    paragraphs below the floor are accumulated, and leftovers under the floor
    are dropped rather than scored unreliably.
    """
    def cap(text: str) -> str:
        words = text.split()
        return text if len(words) <= max_words else " ".join(words[:max_words])

    chunks, buf, count = [], [], 0
    for para in re.split(r"\n\s*\n", prose):
        words = len(para.split())
        if words < 5:
            continue
        buf.append(para)
        count += words
        if count >= min_words:
            chunks.append(cap("\n\n".join(buf)))
            buf, count = [], 0
    if count >= min_words:
        chunks.append(cap("\n\n".join(buf)))
    return chunks


# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------
def load_key(key_file: Path) -> str:
    """Read the key from the environment, a YAML config, or a bare key file.

    A .yaml/.yml source is a config file with the key under `api_key`, so the
    file can carry other settings later; anything else is read as the bare
    key.  The key is never echoed, and never passed on a command line.
    """
    key = os.environ.get("PANGRAM_API_KEY", "").strip()
    if key:
        return key
    if key_file.exists():
        raw = key_file.read_text(encoding="utf-8")
        if key_file.suffix in (".yaml", ".yml"):
            try:
                import yaml
                cfg = yaml.safe_load(raw)
            except ImportError:
                sys.exit(f"{key_file} needs PyYAML to read (pip install pyyaml)")
            if not isinstance(cfg, dict) or not cfg.get("api_key"):
                sys.exit(f"{key_file} has no 'api_key' entry")
            return str(cfg["api_key"]).strip()
        return raw.strip()
    sys.exit(f"no API key: set $PANGRAM_API_KEY or provide {key_file}")


def request(url: str, key: str, payload: dict | None = None, timeout: int = 60):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method="POST" if data else "GET",
        headers={"x-api-key": key, "Content-Type": "application/json"},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"HTTP {exc.code} from {url}: {exc.read()[:400].decode(errors='replace')}")
        except urllib.error.URLError as exc:
            if attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"network error for {url}: {exc}")
    raise SystemExit("unreachable")


def classify(text: str, key: str, model: str, poll_timeout: int = 180) -> dict:
    """Submit one text and poll to completion.  Returns the raw response."""
    submitted = request(f"{BASE_URL}/task", key, {"text": text, "model": model})
    task_id = submitted.get("task_id") or submitted.get("id")
    if not task_id:
        return submitted                      # some deployments answer inline
    deadline = time.time() + poll_timeout
    delay = 1.0
    while time.time() < deadline:
        time.sleep(delay)
        delay = min(delay * 1.5, 8.0)
        result = request(f"{BASE_URL}/task/{task_id}", key)
        stage = str(result.get("stage", "")).upper()
        if "SUCCESS" in stage:
            return result
        if "FAIL" in stage:
            raise SystemExit(f"task {task_id} failed: {json.dumps(result)[:400]}")
    raise SystemExit(f"task {task_id} timed out after {poll_timeout}s")


def trim(result: dict) -> dict:
    """Drop the echoed submission before caching.

    The API returns the full text back, and each window with it.  Caching that
    would copy unpublished prose into a file on disk for no benefit --- the
    text is reproducible from path + chunk index.  Keep a short excerpt per
    window so the worst passages stay identifiable in the report.
    """
    out = {k: v for k, v in result.items() if k != "text"}
    windows = []
    for window in out.get("windows") or []:
        window = dict(window)
        excerpt = (window.pop("text", "") or "")[:160]
        window["excerpt"] = excerpt
        windows.append(window)
    if windows:
        out["windows"] = windows
    return out


def score_of(result: dict) -> float | None:
    """Pull the headline AI fraction out, tolerating schema drift."""
    for key in ("fraction_ai", "ai_likelihood", "ai_assistance_score"):
        value = result.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


# --------------------------------------------------------------------------
# Manifest and safety
# --------------------------------------------------------------------------
def load_samples(manifest_path: Path, allow: set[str]) -> tuple[list[dict], list[str]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    samples, refused = [], []
    for arm, spec in manifest.get("arms", {}).items():
        for entry in spec.get("files", []):
            entry = {"path": entry} if isinstance(entry, str) else dict(entry)
            path = Path(entry["path"]).expanduser()
            if not path.exists():
                refused.append(f"{arm}: {path} does not exist")
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
            hit = SENSITIVE_PATH.search(str(path)) or SENSITIVE.search(raw[:4000])
            if hit and str(path) not in allow:
                refused.append(f"{arm}: {path} matches {hit.group(0)!r} "
                               "(pass --allow-file to override this one file)")
                continue
            entry.update(arm=arm, path=str(path), raw=raw)
            samples.append(entry)
    return samples, refused


def summarize(rows: list[dict], threshold: float) -> None:
    by_arm: dict[str, list[dict]] = {}
    for row in rows:
        by_arm.setdefault(row["arm"], []).append(row)
    print(f"\n{'arm':<10}{'n':>5}{'median':>9}{'mean':>8}{'max':>8}"
          f"{f'>{threshold:g}':>8}")
    print("-" * 48)
    for arm, items in sorted(by_arm.items()):
        scores = [i["score"] for i in items if i.get("score") is not None]
        if not scores:
            print(f"{arm:<10}{len(items):>5}{'--':>9}")
            continue
        flagged = sum(1 for s in scores if s > threshold)
        print(f"{arm:<10}{len(scores):>5}{statistics.median(scores):>9.3f}"
              f"{statistics.fmean(scores):>8.3f}{max(scores):>8.3f}"
              f"{flagged:>8}")
    print("\nworst-scoring chunks (candidates for the residue catalog):")
    for row in sorted((r for r in rows if r.get("score") is not None),
                      key=lambda r: -r["score"])[:8]:
        print(f"  {row['score']:.3f}  {row['arm']:<7} {Path(row['path']).name}"
              f" #{row['chunk']}  {row['words']}w")


# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path, help="JSON manifest of arms -> files")
    ap.add_argument("--submit", action="store_true",
                    help="actually call the API (default is a dry run)")
    ap.add_argument("--self-test", action="store_true",
                    help="check the path refusal against known sensitive shapes")
    ap.add_argument("--check", nargs="+", metavar="FILE",
                    help="score one or more drafts and show which windows "
                         "triggered; appends to the check log")
    ap.add_argument("--check-max-words", type=int, default=1000,
                    help="cap on words sent per --check (billing is per word); "
                         "longer input is truncated with a warning")
    ap.add_argument("--log", type=Path, default=DEFAULT_LOG,
                    help=f"running record of --check results (default: "
                         f"{DEFAULT_LOG})")
    ap.add_argument("--probe", action="store_true",
                    help="submit one sentinel text and dump the raw schema")
    ap.add_argument("--report", action="store_true", help="summarize the cache only")
    ap.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE,
                    help=f"API key file (default: {DEFAULT_KEY_FILE})")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--out", type=Path, default=Path("calibration/out"))
    ap.add_argument("--whole-file", action="store_true",
                    help="submit each file as one passage instead of chunking "
                         "it; use when the files are already curated excerpts")
    ap.add_argument("--min-words", type=int, default=300)
    ap.add_argument("--max-words", type=int, default=1200)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--strip-math", action="store_true")
    ap.add_argument("--no-emacs", action="store_true",
                    help="use the regex fallback instead of Emacs Org export")
    ap.add_argument("--allow-file", action="append", default=[],
                    help="override the sensitivity refusal for one exact path")
    ap.add_argument("--limit", type=int, help="cap chunks per arm (cost control)")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    cache_path = args.out / "cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    if args.check:
        import datetime
        key = load_key(args.key_file)
        logged, log_ok = 0, True
        try:
            args.log.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        except OSError as exc:
            log_ok = False
            print(f"(log unavailable: {exc}. Scores below are printed but not "
                  "recorded; set $PANGRAM_CHECK_LOG or pass --log.)")
        for name in args.check:
            path = Path(name)
            if not path.exists():
                print(f"{name}: no such file")
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
            hit = SENSITIVE_PATH.search(str(path)) or SENSITIVE.search(raw[:4000])
            if hit and str(path) not in args.allow_file:
                print(f"REFUSED {path}: matches {hit.group(0)!r}. This sends text "
                      "to a third party; if it is genuinely yours to send, pass "
                      "--allow-file for this one path.")
                continue
            prose, method = to_prose(path, raw, keep_math=not args.strip_math,
                                     use_emacs=not args.no_emacs)
            words = prose.split()
            if len(words) < PANGRAM_MIN_WORDS:
                print(f"{path}: {len(words)} words is below Pangram's documented "
                      f"{PANGRAM_MIN_WORDS}-word minimum; not sent.")
                continue
            if len(words) < ADVISORY_MIN_WORDS:
                print(f"{path}: {len(words)} words. Above the {PANGRAM_MIN_WORDS}-word "
                      f"minimum but below {ADVISORY_MIN_WORDS}, where accuracy is "
                      "poorer; weigh the result accordingly.")
            if len(words) > args.check_max_words:
                print(f"{path}: {len(words)} words, truncating to "
                      f"{args.check_max_words} (billing is per word). Pass "
                      "--check-max-words to raise, or check one passage at a time.")
            piece = " ".join(words[:args.check_max_words])
            sent = len(piece.split())
            result = classify(piece, key, args.model)
            frac = score_of(result)
            print(f"\n{path}  ({sent} words sent of {len(words)}, via {method}, "
                  f"~${sent * USD_PER_WORD:.2f})")
            print(f"  overall   ai={frac:.3f}  human={result.get('fraction_human', 0):.3f}"
                  f"  assisted={result.get('fraction_ai_assisted', 0):.3f}"
                  f"  -> {result.get('prediction_short', '?')}")
            windows = result.get("windows") or []
            if len(windows) > 1 or (frac or 0) > 0:
                print("  windows (the passage that triggered is the useful part):")
                for w in windows:
                    mark = "  <-- " if w.get("label") != "Human Written" else "      "
                    excerpt = " ".join((w.get("text") or "").split())[:90]
                    print(f"    {w.get('ai_assistance_score', 0):.3f} "
                          f"{str(w.get('label','?')):<16}{mark}{excerpt}")
            if not log_ok:
                continue
            try:
                entry = json.dumps({
                    "when": datetime.datetime.now().isoformat(timespec="seconds"),
                    "path": str(path), "words": len(words), "words_sent": sent,
                    "usd": round(sent * USD_PER_WORD, 4), "fraction_ai": frac,
                    "prediction": result.get("prediction_short"),
                    "windows": [{"score": w.get("ai_assistance_score"),
                                 "label": w.get("label"),
                                 "excerpt": " ".join((w.get("text") or "").split())[:160]}
                                for w in windows]})
                with args.log.open("a", encoding="utf-8") as fh:
                    fh.write(entry + "\n")
                logged += 1
            except OSError as exc:
                print(f"  (not logged: {args.log} is not writable --- {exc}. "
                      "Set $PANGRAM_CHECK_LOG or pass --log.)")
        if logged:
            print(f"\nlogged to {args.log}")
        return 0

    if args.self_test:
        cases = [
            ("/home/coder/mirrors/Admin/Referee/REStud/Kinnan14/report.org", True),
            ("/home/coder/mirrors/Admin/Correspondence/referee/notes.org", True),
            ("/home/coder/mirrors/Admin/Letters/ChenJoyce/promotion.tex", True),
            ("/home/coder/mirrors/Admin/Committees/Adhoc/Magruder/Tenure/x.org", True),
            ("/home/coder/mirrors/Admin/Committees/Department/Search/2021/notes.org", True),
            ("/home/coder/mirrors/Admin/Employment/Review/2005/self-evaluation.tex", True),
            ("/home/coder/mirrors/VESDemand/Editorial/aer_revisions.org", True),
            ("/home/coder/mirrors/Students/KjorlienScott/report.org", True),
            ("/home/coder/mirrors/Admin/Credentials/key.json", True),
            ("/home/coder/mirrors/VESDemand/Text/tracking_neediness.org", False),
            ("/home/coder/mirrors/VESDemand/Text/notes.org", False),
            ("/home/coder/mirrors/ARE201/Readings/supply.org", False),
        ]
        bad = 0
        for path, expected in cases:
            got = bool(SENSITIVE_PATH.search(path))
            if got != expected:
                bad += 1
                print(f"FAIL  expected {'refuse' if expected else 'allow'}: {path}")
        print(f"{len(cases)} path case(s), {bad} failure(s)")
        return bad

    if args.probe:
        key = load_key(args.key_file)
        print("GET /models ->", json.dumps(request(f"{BASE_URL}/models", key))[:600])
        sentinel = ("The estimator is consistent under the stated assumptions. "
                    "We verify this in simulation. ") * 12
        print("\nPOST /task ->")
        print(json.dumps(classify(sentinel, key, args.model), indent=2)[:2000])
        return 0

    if args.report:
        rows = [r for r in cache.values() if isinstance(r, dict) and "arm" in r]
        if not rows:
            print("cache is empty; run with --submit first")
            return 1
        summarize(rows, args.threshold)
        return 0

    if not args.manifest:
        ap.error("--manifest is required (or use --probe / --report)")

    samples, refused = load_samples(args.manifest, set(args.allow_file))
    for message in refused:
        print(f"REFUSED  {message}")

    rows, pending = [], 0
    per_arm: dict[str, int] = {}
    for sample in samples:
        prose, _method = to_prose(Path(sample["path"]), sample["raw"],
                                  keep_math=not args.strip_math,
                                  use_emacs=not args.no_emacs)
        # Chunking a file that is ALREADY a curated excerpt silently drops the
        # tail: chunk() emits at the first paragraph boundary past --min-words
        # and discards a remainder below that floor, so two arms holding the
        # same passage can be scored on different fractions of it.
        pieces = ([" ".join(prose.split()[:args.max_words])] if args.whole_file
                  else chunk(prose, args.min_words, args.max_words))
        for i, piece in enumerate(pieces):
            if args.limit and per_arm.get(sample["arm"], 0) >= args.limit:
                break
            per_arm[sample["arm"]] = per_arm.get(sample["arm"], 0) + 1
            digest = hashlib.sha256(
                f"{args.model}\n{piece}".encode()).hexdigest()[:16]
            row = {"arm": sample["arm"], "path": sample["path"], "chunk": i,
                   "words": len(piece.split()), "digest": digest,
                   "added": sample.get("added"), "genre": sample.get("genre")}
            if digest in cache:
                # Reuse the SCORE, not the cached row: the cache is keyed by
                # text alone, so a passage submitted under one arm and reused
                # under another would otherwise report the first arm's label.
                hit = cache[digest]
                row["score"] = hit.get("score")
                row["prediction"] = hit.get("prediction")
                row["raw"] = hit.get("raw")
                rows.append(row)
                continue
            pending += 1
            if not args.submit:
                rows.append(row)
                continue
            result = classify(piece, load_key(args.key_file), args.model)
            row["score"] = score_of(result)
            row["prediction"] = result.get("prediction_short")
            row["raw"] = trim(result)
            cache[digest] = row
            cache_path.write_text(json.dumps(cache, indent=1))
            rows.append(row)
            print(f"  {row['score']!s:>6}  {sample['arm']:<7} "
                  f"{Path(sample['path']).name} #{i} ({row['words']}w)")

    cached = len(rows) - pending
    print(f"\n{len(samples)} file(s), {len(rows)} chunk(s): "
          f"{cached} cached, {pending} {'submitted' if args.submit else 'would be submitted'}")
    for arm, n in sorted(per_arm.items()):
        print(f"  {arm:<10}{n:>4} chunk(s)")
    if not args.submit:
        print("\nDRY RUN --- nothing was sent. Re-run with --submit to spend "
              f"{pending} API call(s).")
        return 0
    summarize([r for r in rows if r.get("score") is not None], args.threshold)
    return 0


if __name__ == "__main__":
    sys.exit(main())

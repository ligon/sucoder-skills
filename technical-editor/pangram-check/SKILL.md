---
name: pangram-check
description: >-
  Use this skill to score a draft with the Pangram AI-text detector, see which
  passage reads as machine-written, and log the result so patterns accumulate
  across checks. It trips on user cues like "check this for AI", "does this
  read as AI-generated?", "run pangram on this", "is this detectable?", "score
  this draft", or "what has been firing in the check log". It is a diagnostic,
  NOT a quality measure and NOT a gate to rewrite against: a nonzero score
  localizes a passage worth reading, a zero means little, and neither rate is
  well estimated yet. Do NOT use on confidential material --- referee reports,
  editorial correspondence, personnel or student files, or coauthored and
  unpublished work that is not yours alone to send.
license: Apache-2.0
---

# Pangram Check

Score a draft with an external AI-text detector, localize the passage that
triggered it, and log the result so that patterns accumulate across many
checks.

## When to Use (and when NOT to)

Apply this skill when:
- A draft needs checking for whether it reads as machine-written.
- A flagged passage needs localizing, so the prose fault can be named.
- The accumulated check log needs reviewing for patterns worth promoting
  into the residue catalog.

Do NOT apply this skill:
- To decide whether prose is any GOOD.  The detector does not measure that,
  and in testing its verdict and the author's quality judgement diverged.
- As a gate in a drafting loop, or to rewrite against until a draft passes.
- To anything confidential --- see the section below, which is the one
  constraint here with no judgement calls in it.

## How much confidence the numbers support: very little so far

Two observed rates, both from small samples, neither one an established
property of the detector:

- 26 of 26 passages of pre-LLM single-authored prose scored 0.000.  That is
  consistent with a true false-positive rate anywhere up to about 11 percent
  at 95 percent confidence, and the sample is one author, one genre, one era,
  all passages 300--480 words.
- 4 of 12 machine-written passages also scored 0.000, so the miss rate is
  estimated from twelve observations and could plausibly be anywhere from
  roughly 15 to 65 percent.

Pangram reports a false-positive rate around 1 in 10,000 and a 2025
University of Chicago Booth audit found near-zero false positives on longer
passages.  That is real external evidence and a reason to expect the rate to
be low --- but it was measured on other corpora, not on this genre, and it
does not license treating our 26 observations as a settled distribution.

The working posture, held provisionally: a nonzero score is more likely to be
worth reading than a zero is to be reassuring, because the observed
false-positive rate is lower than the observed miss rate.  How much more
likely, nobody here knows.  Do not convert that into a rule that a hit proves
something and a pass proves nothing.

This is exactly what the running log is for.  Every check, including
deliberate controls on prose you know you wrote unaided, adds an observation.
After enough of them the two rates stop being guesses, and only then is it
worth asking what a given score actually implies.

## Do not iterate against the score

Do not rewrite a draft to lower its number, and do not resubmit in a loop
until it passes.  Three reasons --- the first two observed once, in a small
test, and the third structural rather than empirical:

1. The detector measures whether a machine wrote the text, not whether the
   text is good.  Those objectives come apart.  In a blinded test, the
   author rated one undetected machine passage the best prose in the set,
   and rated one of his own passages below it.
2. In that same test the author and the detector disagreed on four of six
   machine-written passages, each catching things the other missed.  Six
   pairs cannot establish a rate, but they do show the two judgments are not
   measuring one thing.
3. Optimizing prose against a classifier optimizes for evading the
   classifier.  The goal is better prose; evasion is a different goal that
   happens to be easier to measure.

## What it is actually good for

- LOCALIZING.  The per-window output shows which passage fired.  That is the
  part you can learn from --- read the flagged window and ask what is wrong
  with it in prose terms.
- ACCUMULATING.  Every check appends to the running log (see below) with the
  score, the verdict, the words sent, the cost and the flagged excerpts.  One score tells you little; twenty checks showing the same
  construction firing repeatedly is a pattern worth naming.
- FEEDING THE CATALOG.  When a construction recurs across several checks,
  name it and add it as a new id in
  `file:../../ligon-voice/references/agent-residue.org`, then propagate it to
  both `research-writer/SKILL.md` and `technical-editor/SKILL.md`.
  `make check` enforces that all three stay in sync.  The named rule is the
  durable artifact; the score is not.

## Confidentiality (non-negotiable)

This sends text to a third party.  Never submit referee reports on other
people's papers, editorial correspondence reproducing a journal's decision
letter or referee reports, unpublished coauthored work without the
coauthors' agreement, recommendation or tenure letters, or student records.

The tool refuses these by path (`Referee/`, `Letters/`, `Adhoc/`,
`Editorial/`, `Students/`, `Employment/Review/`, and others) and by content
markers, and the refusal names a single-file override rather than a blanket
one.  If a refusal fires, the default answer is to not send the text.

## Usage

The script lives at the skills-repo root, not beside this file, because the
calibration workflow uses it too.  Invoke it by absolute path --- a draft
being checked is rarely in the skills repo, and a relative path silently
resolves against wherever the draft happens to live.  Substitute the local
mirror root for SKILLS (`/home/ligon/.sucoder/skills` on the human's
account, `$(sucoder path skills)` or the mirror checkout otherwise).

#+begin_src bash
# score one or more drafts
python3 SKILLS/scripts/pangram_calibrate.py --check draft.org

# several at once, including a control of your own older prose
python3 SKILLS/scripts/pangram_calibrate.py --check draft.org known_human.org

# review what has fired over time; --help prints the resolved log path
LOG=$(getent passwd coder >/dev/null && echo ~coder || echo ~)/.sucoder/pangram/check_log.jsonl
python3 -c 'import json,sys
for r in map(json.loads, open(sys.argv[1])):
    print(round(r["fraction_ai"], 3), r["path"])' "$LOG"
#+end_src

The API key comes from `$PANGRAM_API_KEY`, else `--key-file`.  Its default
resolves the OPPOSITE way from the log: the key is a credential the human
downloaded, so it looks in the home of the account named by `human_user` in
`~/.sucoder/config.yaml` (in practice `/home/ligon/Downloads/pangram_api_key`)
before falling back to the caller's home.  Writing it as `~/Downloads` would
be wrong --- on an agent session `~` is the one account the key is not in.
`--help` prints the resolved path.

Org files are exported to plain text with Emacs before submission, so the
detector scores prose rather than markup.

## Where the key lives

Never in the repository.  The key is read at run time from a path outside
every git tree, and no committed file, cache or log has ever contained the
value.

It lives in a per-account config file:

#+begin_src yaml
# /home/coder/.sucoder/pangram/config.yaml   (mode 0600, dir 0700)
api_key: sk-...
#+end_src

Resolution order, first hit wins:

1. `$PANGRAM_API_KEY`
2. `--key-file`
3. `<human-account-home>/.sucoder/pangram/config.yaml`
4. `<caller-home>/.sucoder/pangram/config.yaml`
5. the same two paths with a bare `api_key` file instead of `config.yaml`
6. `<home>/Downloads/pangram_api_key`  (legacy, see below)

A `.yaml`/`.yml` source is parsed and the key read from `api_key`, so the
file can carry further settings later; any other path is read as a bare key.
`--help` prints whichever path resolved.

The Downloads entries remain only so an older setup keeps working, and a
credential does not belong there.  On this workspace `~/Downloads` is a 9p
mount shared with the host OS, where Unix modes are not reliably enforced,
and the file is world-readable --- which is the only reason the agent
account can read it at all, since that account is not in the human's group.
Tightening that file to 0600 would break agent sessions rather than secure
anything, so the fix is to move the key, not to re-permission it.

Note that the config file sits in the AGENT account's home, because that is
the account sessions run under.  A human invoking the tool directly under
their own login will not read it, and needs `$PANGRAM_API_KEY`, `--key-file`,
or a copy under their own `~/.sucoder/pangram/`.

## Where the log lives, and why there

`<agent-account-home>/.sucoder/pangram/check_log.jsonl` --- in practice
`/home/coder/.sucoder/pangram/check_log.jsonl` --- absolute, outside every git
tree, in a directory created mode 0700.  The default resolves to the `coder`
account's home when that account exists, and to the caller's home when it does
not.  `--help` prints the resolved path.  `$PANGRAM_CHECK_LOG` overrides it and
`--log` overrides that.

The location is deliberate on three counts.  The log is only useful as ONE
file, so a path relative to the working directory would fragment it per repo,
and keying it to the caller's home would fragment it per account --- sessions
run under the shared agent account, but a human may run the same check
directly, and those observations belong in the same file.  And it accumulates
excerpts of whatever is checked, including unpublished drafts: written under a
research mirror it would sooner or later be committed into a paper repo whose
`.gitignore` knows nothing about it.

If the log is not writable the check still runs and prints its score, with a
notice that the result was not recorded.

## How much text to send

Billing is per word, at $0.05 per 100 words, and the detector needs context
to predict at all.  Both bounds matter.

- FLOOR :: 50 words is Pangram's documented minimum and the tool refuses
  below it.  Below roughly 300 words the result is weak rather than merely
  noisy, and the tool says so; weigh it accordingly rather than acting on it.
- CEILING :: the default cap is 1000 words per check, about $0.50.  Longer
  input is truncated with a warning; `--check-max-words` raises it.
- IN PRACTICE :: send the passage you are actually unsure about, roughly
  300--800 words.  Submitting a whole draft to ask about one paragraph pays
  for every other paragraph and buries the window you cared about among
  windows you did not.  A 5,000-word section costs about $2.50 per check, and
  checking it repeatedly during revision multiplies that.

Each check prints the words sent and the estimated cost, and both are
recorded in the log.

## Mechanics that affect validity

- Markup: never submit raw LaTeX or Org.  Markup is not prose and the
  comparison to human text stops being like-for-like.  The tool normalizes
  automatically; if you paste text in by hand, strip it yourself.
- Control: score a passage of your own older writing every so often.  These
  controls are not ceremony --- they are what turns the two guessed rates
  above into estimates, and a nonzero result on known-unaided prose would be
  the single most informative observation the log could record.

## Related Skills

- `file:../SKILL.md` --- the editor this diagnostic serves.
- `file:../../ligon-voice/references/agent-residue.org` --- where a pattern
  goes once it has recurred often enough to name.

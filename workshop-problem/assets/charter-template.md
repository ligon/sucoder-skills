# Workshop Charter — <problem name>

> The contract for working a problem. Agreed with the human in phases 0–1
> (scope + red-team) BEFORE implementation. The engine (phases 2–6) treats §2 as
> the oracle it loops against — "green" means every criterion in §2 is satisfied.
> Git-track this file and edit it in place; the commit history is the journal.

## §0 Question, restated
<The problem in the human's own words, AFTER red-teaming the framing. If this
restatement surprises the human, phase 0 is not finished. Note any premise you
challenged and how it was resolved — including problems found in the *original*
framing.>

## §1 Scope & non-goals
**In scope:**
- <...>

**Out of scope / non-goals:**  (this list is what stops scope creep)
- <...>

## §2 Definition of done  — the loop oracle; make every line decidable
The work is complete when ALL of the following hold. Prefer criteria a test or a
measurement can decide; for a judgement call, name *who* decides it.

- [ ] <criterion — e.g. "estimator matches `stats.effective_dof` on fixture X to 1e-8">
- [ ] <criterion — e.g. "runs in < 2 s on the 10k-row fixture">
- [ ] <criterion — e.g. "new public function has a passing test in `test_*.py`">
- [ ] <criterion — e.g. "result reviewed and accepted by <name>">  ← judgement call

## §3 Constraints & assumptions
- **Budget:** <time / compute>
- **Tools allowed:** <...>
- **Data available:** <...>
- **Must not break:** <backward-compat, existing tests, public API>
- **Conventions to honor:** <style, local definitions — see §4 ledger>

## §4 Links
- **Prior-art ledger:** <path, if this is code-in-a-repo — see `prior-art-ledger`>
- **Relevant prior work / issues / papers:** <...>

## §5 Open questions & risks
Anything still ambiguous or load-bearing. Phase 2 (Ground) may add to this and
**kick the problem back to the human** rather than guess.

- <question — and what decision it blocks>

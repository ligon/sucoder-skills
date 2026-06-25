---
name: prior-art-ledger
description: Use this skill at the start of a non-trivial task in an existing code repository, BEFORE adding an estimator, function, or analysis. It forces an explicit inventory of the "terms of the debate"—existing tested utilities, definitions, and conventions already in force—then requires the work to cite that inventory, then checks the result against it. Targets the failure mode where an agent reinvents an existing tested method (e.g., effective degrees of freedom) or contradicts a local definition. The ledger is a git-tracked living document, so grounding compounds across sessions. Lightweight, prompt-discipline only; no orchestration.
license: Apache-2.0
---

# Prior-Art Ledger

A discipline for working inside a repository whose terms are already set. The
core artifact is a **ledger**: a short, git-tracked inventory of the existing
machinery, definitions, and conventions that bear on the task. The ledger is
read and updated *before* the work, kept in context *during* the work, and is
the *only* oracle the verification step trusts.

The point is not to review code in general. It is to catch two specific
failures: (1) reinventing something the repo already implements and tests, and
(2) contradicting a definition, assumption, or convention already in force.

## When to Use

Load this skill when, in an existing repo, you are asked to:
- Add an estimator, statistic, transformation, or model component.
- Implement an analysis that computes a quantity the codebase may already compute.
- Extend or modify a method whose correct behavior depends on local definitions.

Do **not** bother for greenfield code, throwaway scripts, or one-line fixes.

## The Anchor Principle

A generic "review this" pass will *not* catch a reinvented `effective_dof`—the
reviewer knows no more about the repo than the author did. So verification here
checks the work **against the ledger**, not against the model's own priors.
Build the ledger well and the rest follows; build it poorly and the checks are
theater.

## Tooling — use the best available, never block on it

Detect what this repo and host offer; use the highest tier present. `git` and
`ripgrep` are the floor and are assumed always available. gitnexus and cq are
accelerators—their absence degrades search *quality*, not correctness.

- **Symbols, call sites, dependents** (for ledger §2):
  1. gitnexus (`mcp__gitnexus__query` / `cypher`) if the repo is indexed — best
     for "what calls / depends on this".
  2. An LSP or tags index (`pyright`, `pylsp`, `ctags -R`) for defs/refs.
  3. `ripgrep` over identifiers + concept synonyms, plus AST search
     (`ast-grep`, or `python -m ast`) — always works.
- **Cross-session memory:**
  1. The git-tracked ledger (always; see Persistence).
  2. cq commons (`mcp__plugin_cq_cq__query` / `propose`) if present — for
     *transferable* pitfalls only, not repo-specific definitions.

Record in the ledger which tier you used, so a later session knows how thorough
the search actually was.

## Persistence — current-state ledger + git as the journal

The ledger is a **living, git-tracked file** (default `.coder/ledger.md`; pick a
path that fits the repo and keep it stable once chosen). It always reflects
*current* understanding—edit it in place, do not append a running log.

- **At task start**, if the ledger exists: read it, then skim
  `git log -p -- <ledger>` and recent commit subjects to see how and why it
  reached its current state before trusting or revising it. The history is the
  journal; the file is the snapshot.
- **At task end**, commit the updated ledger in its **own** commit with a
  message that explains the change (e.g. `ledger: effective_dof lives in
  stats.py:212; mark task quantity as reuse`). Those messages are the journal
  entries—don't maintain a separate append log, and don't bundle ledger edits
  with code changes.
- Keep repo-specific terms in the ledger. When cq is available, push only
  *transferable* lessons there (e.g. "this estimator family assumes demeaned
  inputs"), not local file paths.

## Phase 1 — Ground (build or refresh the ledger)

Read-only except for the ledger file. Do not write task code yet. This is the
highest-leverage step and the one the human should review.

Read the existing ledger and its git history first (see Persistence), then for
each thing the task will need to compute or assume, fill in or update:

1. **Task, restated.** One paragraph in the repo's own vocabulary. If you can't
   restate it without inventing terms, you don't understand it yet.
2. **Existing machinery.** Every function/class/module that already touches this
   area. For each: `path:line`, a one-line description, and **whether it is
   tested** (name the test). Use the best available search tier (see Tooling)
   and note which tier you used. This is where reuse lives—search the concept
   and its synonyms, not just the obvious identifier.
3. **Definitions & conventions in force.** The precise *local* meaning of the
   key terms (notation, units, sign conventions, indexing, what "degrees of
   freedom" / "residual" / "weight" means *here*). Quote the source `path:line`
   or paper section—do not paraphrase from memory.
4. **Invariants & assumptions.** What must hold for the existing code to be
   correct (demeaned inputs? full rank? a particular estimator family?). These
   are the landmines.
5. **Reuse decision.** For each quantity the task needs: does it already exist?
   Mark **reuse / extend / new**, with a one-line reason. "new" requires
   justifying why the existing thing doesn't fit.
6. **Open questions for the human.** Anything ambiguous or load-bearing.

Then **stop and surface the ledger to the user** before implementing. Cheap
review here prevents expensive rework.

## Phase 2 — Act

Implement with the ledger in context. Constraints:
- Prefer **reuse / extend** over **new**; if you write something marked "new" in
  the ledger, restate the reason in the code or commit message.
- Honor the definitions and invariants verbatim. Match local naming and style.
- Annotate each non-trivial new piece with the ledger entry it relies on
  (e.g., `# reuses stats.effective_dof (ledger §2)`).

## Phase 3 — Verify against the ledger

Anchored check, not a general review. For each new or changed symbol:
- **Reuse check.** Search the repo again (best available tier) for a prior
  implementation of what it computes—by formula, not just by name, since
  reinvented methods rarely share a name. If one exists and is tested, the new
  code must justify its existence or be replaced by a call to it.
- **Definition check.** Confirm the work matches every definition/convention in
  ledger §3 and violates no invariant in §4. Cite the entry for each check.
- **Test check.** New behavior gets a test; reused behavior should already be
  covered—confirm and run the relevant tests.

Report findings as: `CONTRADICTION` (violates a ledger entry), `REINVENTION`
(duplicates existing tested code), or `OK (anchored on §N)`. Anything not tied
to a ledger entry is out of scope for this pass—say so rather than padding.

## Pitfalls / escalation

- **Weak ledger = useless checks.** If Phase 1 can't find the relevant
  machinery or pin the definitions, say so and ask the human—don't proceed on a
  guess. Incorrect context is worse than missing context.
- **Don't trust an unanchored critic.** A finding with no ledger citation is a
  prior, not evidence.
- **Don't let a tool's absence stop you.** gitnexus/cq missing → drop to the
  ripgrep/git floor and note the lower tier; never block.
- **Keep it lean.** This is prompt discipline, not orchestration. If a task is
  large enough to want parallel finders and adversarial verification, that's the
  heavier `Workflow`-backed successor to this skill—escalate rather than bloat
  this one.

## Changelog

- ## <2026-06-25 Thu> Initial draft. Empirical-package case (reuse / convention
  / definition). Lightweight, single-file, no orchestration. Tools (gitnexus,
  cq) optional with a git+ripgrep floor; ledger is git-tracked with history as
  the journal.

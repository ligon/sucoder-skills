---
name: workshop-problem
description: Use this skill when handed a non-trivial technical problem open-endedly — "here's a hard problem, see what you can do with it." Runs a gated lifecycle: scope and red-team the question (the human's framing included), agree a written charter with a checkable definition-of-done, ground in prior art, implement, adversarially red-team, loop until green on the charter, then review. Phases 0–1 are a human handshake; phases 2–6 can run autonomously via the bundled workflow. Delegates to prior-art-ledger (grounding), code-reviewer / technical-editor (review), and test-generator (tests) rather than duplicating them. Right-size the ceremony — skip it for trivia.
license: Apache-2.0
---

# Workshop a Problem

A conductor for the open-ended ask: *"here's a non-trivial technical problem —
see what you can do with it."* The danger in that ask is not the work; it's
starting the work before the **question** is agreed and before *done* is
**defined**. This skill front-loads both, grounds the attempt in what already
exists, then drives an adversarial implement→red-team→converge loop until the
result meets a written bar.

The spine is a single carrier artifact, the **charter** (`assets/charter-template.md`):
the agreed question, its scope, and a *checkable* definition-of-done. The
charter is written with the human in phases 0–1 and is the **oracle** the later
phases loop against — "green" means every criterion in the charter's §2 holds.

## When to Use

Load this skill when the task is **open-ended and non-trivial**: a research
question, a new estimator or analysis, a design with real choices, anything
where the framing itself could be wrong. The user story is "do something useful
with this," not "make this specific edit."

**Right-size the ceremony.** Do *not* run the full lifecycle for a typo, a
one-line fix, a mechanical rename, or a task whose scope and success are already
obvious. For those, the phases collapse to nothing — just do the work. The
heavyweight version earns its cost only when getting the *question* wrong is a
live risk.

## The Shape

| Phase | What happens | Mode | Delegates to |
|------:|--------------|------|--------------|
| 0 | **Scope & red-team the question** — challenge the framing, surface the human's mistakes | conversational | — |
| 1 | **Agree the charter** — scope, non-goals, checkable definition-of-done; get explicit sign-off | conversational (gate) | — |
| 2 | **Ground** — inventory existing machinery, definitions, conventions; early-exit on blockers | engine | `prior-art-ledger` |
| 3 | **Implement** — attempt the solution against charter + ledger | engine | `test-generator` (tests) |
| 4 | **Red-team** — adversarially try to break (3) against the charter | engine | — |
| 5 | **Converge** — loop 3↔4 until green on the charter (with a hard cap) | engine | — |
| 6 | **Review** — final adversarial / PR-style review | engine | `code-reviewer`, `technical-editor` |

Phases **0–1 are a human handshake** and stay in conversation — a background
process cannot re-negotiate scope. Phases **2–6 are the engine** and, in Claude
Code, can run autonomously via the bundled workflow (below).

## Phase 0 — Scope & red-team the question

Before agreeing to *anything*, interrogate the framing. The person handing you
the problem makes mistakes too; your first job is to catch them while they are
cheap.

- Restate the problem in your own words and play it back. If your restatement
  surprises them, the question is not yet understood.
- Challenge the premise: Is this the real problem or a symptom? Is the implied
  approach assuming a conclusion? What would make this question *not worth
  answering*?
- Probe scope edges: what is tempting to include that should be a non-goal?
- Name what a *resolution* would even look like — this seeds §2.

Surface disagreements now, plainly. This is the cheapest red-team in the whole
lifecycle.

## Phase 1 — Agree the charter (gate)

Copy `assets/charter-template.md` to a git-tracked path (e.g. `.coder/charter.md`)
and fill it in *with* the human:

- **§0 Question, restated** — in their vocabulary, after phase 0.
- **§1 Scope & non-goals** — the non-goals are what stop scope creep later.
- **§2 Definition of done** — the heart of it. Write each criterion so a test,
  a measurement, or a named person can *decide* it. Vague criteria make
  "converge until green" meaningless.
- **§3 Constraints & assumptions**, **§4 Links** (→ prior-art ledger if this is
  code-in-a-repo), **§5 Open questions**.

**This is a gate.** Get explicit human sign-off on the charter before
implementing. In Claude Code, use *plan mode* (`EnterPlanMode` / `ExitPlanMode`)
to present the charter and hold for approval — don't reinvent the handshake.

## Phases 2–6 — Run the engine

Once the charter is signed off, run the engine. In **Claude Code**, invoke the
bundled workflow and pass the charter as `args`:

```
Workflow({
  scriptPath: "<this skill dir>/assets/workflow.js",
  args: { charter: "<full text of the agreed charter>",
          ledgerPath: ".coder/ledger.md",   // optional; created if code-in-a-repo
          maxIterations: 3 }
})
```

In **any other harness** (or for a small problem), run the same phases by hand:

- **2 Ground.** Apply `prior-art-ledger` — build/refresh the ledger of existing
  tested machinery, definitions, and invariants. *Early-exit rule:* if grounding
  surfaces a blocking unknown or shows the charter is mis-scoped, **stop and
  return to the human** (phase 0/1) rather than guessing. The engine red-teams
  the framing by kicking it back, not by plowing ahead.
- **3 Implement.** Attempt the solution with charter + ledger in context. Prefer
  reuse/extend over new (per the ledger). Add tests via `test-generator`.
- **4 Red-team.** Adversarially attack (3) **against the charter's §2** — try to
  show a criterion fails, an assumption is violated, an edge case breaks it. Use
  independent skeptics; default to "not yet" when uncertain.
- **5 Converge.** Evaluate against every §2 criterion. If all green and the
  red-team found nothing surviving, done. Otherwise feed the findings back to
  (3) and repeat — up to a hard iteration cap. If the cap is hit without green,
  report *honestly* as not-converged with the open criteria; do not declare
  victory.
- **6 Review.** Final adversarial pass: `code-reviewer` for code,
  `technical-editor` for prose. Surface residual risks for human sign-off.

When the problem is large enough to want parallel finders and multi-vote
adversarial verification, the workflow already provides it; escalate breadth
there rather than bloating phases by hand.

## Delegation map

This skill is a conductor — it *sequences and gates*, it does not re-implement
its siblings.

- **Ground (2)** → `prior-art-ledger`
- **Tests (3)** → `test-generator`
- **Red-team / Review (4, 6)** → `code-reviewer` (code) · `technical-editor` (prose)
- **Parallel fan-out / dispatch** → `scrum-master-hpc` if work needs splitting
  across many agents/nodes.

## Pitfalls / escalation

- **Skipping phase 0 is the expensive mistake.** A flawless answer to the wrong
  question is the most costly outcome here. Most of this skill's value is in 0–1.
- **Uncheckable §2 = a loop that never converges (or converges on nothing).**
  If you cannot make a criterion decidable, say so in §5 and name who judges it.
- **The engine cannot re-scope.** A workflow runs to completion; it must
  early-exit and surface, never silently reinterpret the charter.
- **Don't dress up trivia.** If the right-size guard says "just do it," do it.
  Ceremony applied to small tasks reads as diligence but is waste.

## Related Skills

- `prior-art-ledger` (`../prior-art-ledger/SKILL.md`) — the grounding discipline
  phase 2 runs; its ledger is linked from charter §4.
- `code-reviewer` (`../code-reviewer/SKILL.md`) — the defect pass for phases 4/6
  on code.
- `technical-editor` (`../technical-editor/SKILL.md`) — the adversarial pass for
  phases 4/6 on prose.
- `test-generator` (`../test-generator/SKILL.md`) — tests for phase 3.
- `scrum-master-hpc` (`../scrum-master-hpc/SKILL.md`) — when implementation needs
  parallel dispatch across agents/nodes.

## Changelog

- **<2026-06-25 Thu>** — Initial draft. Gated 0–6 lifecycle: human handshake
  (0–1) producing a charter, then an autonomous engine (2–6) that grounds,
  implements, red-teams, converges on the charter, and reviews. Conductor that
  delegates to prior-art-ledger / code-reviewer / technical-editor /
  test-generator; bundled Claude Code workflow for phases 2–6; right-size guard
  for trivia.

# Prior-Art Ledger — <repo or task name>

> Living, git-tracked snapshot of the machinery, definitions, and conventions
> that bear on the current task. Reflects *current* understanding — edit in
> place, do not append a running log (git history is the journal). The section
> numbers below match the `§N` citations used in code comments and Phase 3
> verification reports; keep them.

**Search tier used:** <gitnexus | LSP/ctags | ripgrep+AST>  — see SKILL.md "Tooling"

## §1 Task, restated
<One paragraph in the repo's own vocabulary. If you can't restate it without
inventing terms, you don't understand it yet.>

## §2 Existing machinery
Every function/class/module that already touches this area. Search the concept
*and its synonyms*, not just the obvious identifier.

| symbol | path:line | what it does | tested? (test name) | reuse / extend / new |
|--------|-----------|--------------|---------------------|----------------------|
| `effective_dof` | `stats.py:212` | trace of the hat matrix | yes — `test_stats.py::test_effective_dof` | reuse |

## §3 Definitions & conventions in force
Precise *local* meaning of the key terms. Quote the source `path:line` or paper
section — do not paraphrase from memory.

- **degrees of freedom**: n − trace(H), per `stats.py:200` docstring (not n − p).
- **residual**: <local meaning>, `path:line`.

## §4 Invariants & assumptions
What must hold for the existing code to be correct — the landmines.

- Inputs are demeaned before entering `stats.*` (`stats.py:40`).
- Design matrix assumed full rank (`stats.py:188`).

## §5 Reuse decision
For each quantity the task needs. "new" must justify why the existing thing
doesn't fit.

| quantity | decision | reason |
|----------|----------|--------|
| effective d.o.f. | reuse | `stats.effective_dof` exists and is tested |

## §6 Open questions for the human
Anything ambiguous or load-bearing.

- <question — and what decision it blocks>

---
name: working-with-github
description: >-
  Use this skill when driving a GitHub repository through `gh` or git: writing a
  commit message or PR body that references an issue, merging a PR, or reading a
  red CI run on a PR you just opened. It carries only traps that have already
  cost a session — properties of GitHub's own parsing and of CI that are not
  discoverable from `gh --help` or from reading the code — and deliberately does
  not restate the `gh` manual.
license: Apache-2.0
---

# Working with GitHub

## When to Use

Load this before:
- Writing a commit message or PR body that mentions an issue number.
- Merging a PR, or deciding what the merge commit will say.
- Debugging a red CI run on a PR you just opened.

## Closing keywords are tokens, not intent

GitHub closes an issue when a commit message that lands on the default branch
contains `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`,
`resolves` or `resolved` followed by `#N`. It does not parse the surrounding
English.

This merge commit body closed the issue it was disclaiming:

```
Merge: say when WIP retention could not check a snapshot's job (#14)

Makes the bound observable; does not close #14.
```

`does not close #14` contains `close #14`. The disclaimer did the closing
(ligon/sucoder commit `c6e1a8bd`, the merge of PR 31; issue #14 had to be
reopened).

So: **never let a closing keyword sit next to an issue reference in a commit
message**, whatever the sentence around it says. To mention an issue in
passing, write `issue 14`, or `ligon/sucoder#14` with no keyword in front of
it. Keep `Closes #N` in the PR description, where it takes effect only at
merge.

### Why the rule that existed did not bind

sucoder already had a rule covering this: *put `Closes #N` only in the PR body,
never in a commit message, unless the commit really does close the issue.* It
did not prevent the failure. The rule is phrased around intent, and the
offending sentence had the opposite intent — an agent checking a draft against
it concludes "this commit does not close the issue, so the rule does not apply"
and commits the string anyway.

A rule that asks what you meant cannot catch a parser that sees only what you
typed. When the failure mode is lexical, phrase the rule lexically: name the
token, not the intention.

## Two closing mechanisms, and a disclaimer cancels neither

They are separate, and confusing them is what makes the trap above look
survivable:

- A closing keyword in the **PR description** links the issue to the PR, and
  GitHub closes it when the PR merges.
- A closing keyword in **any commit message** reaching the default branch closes
  the issue on its own, whether or not a PR was involved.

A PR body reading "this does not close #14" is inert against the second. It is
not part of any commit, and nothing reads it as a cancellation. sucoder has been
bitten here twice: in PR 21, and again in PR 31 as above.

Before merging, read the text that will actually become the merge or squash
commit, not the text sitting in the PR description field. A squash merge in
particular composes its body from the PR and its commits, so a sentence written
for the description can end up in commit text after all.

## Red CI is not necessarily yours

A PR opened against a red `main` inherits the red. Establish whether the
failures predate your change before debugging your own diff:

```sh
gh run list --repo <repo> --branch main --limit 8
gh run view <run-id> --log-failed | grep FAILED
```

In the seeding session this turned a suspected regression into a 21-hour-old
breakage from an unrelated merge. The fix then belonged in its own PR rather
than folded into the one under review, and posting the diagnosis as a comment
on the PR stopped a reviewer reading the red X as the change's fault.

## Not in this skill yet

Absent until a session pays for them:
- what `gh pr merge` does and does not carry into the merge commit, beyond the
  closing-keyword case above;
- waiting on checks without polling badly;
- when to comment on a PR versus amending its body.

Add an entry only together with the failure that produced it. Guesses dilute
the rules that are not guesses.

## Related Skills
- `code-reviewer` (`../code-reviewer/SKILL.md`) — what to look for in the diff
  once the PR mechanics here are right.
- `scrum-master-hpc` (`../scrum-master-hpc/SKILL.md`) — branch and worktree
  discipline upstream of opening a PR at all.
- `document-skill` (`../document-skill/SKILL.md`) — the house shape this file
  follows when you extend it.

## Changelog
- **<2026-09-22 Tue>** — Initial draft, from sucoder-skills #6. Seeded by one
  sucoder session (ligon/sucoder#14, #27, #28, PRs 29-31) plus the earlier
  PR 21 instance; the disclaiming merge commit was verified as `c6e1a8bd`.

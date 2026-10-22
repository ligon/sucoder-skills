---
name: skill-feedback
description: Use this skill when using any sucoder skill reveals a bug, unclear or conflicting instruction, missing capability, or useful improvement. Agents are encouraged to report actionable feedback, feature requests, and bug reports as GitHub issues on ligon/sucoder-skills, checking existing reports first.
license: Apache-2.0
---

# Feedback on sucoder skills

## Trigger

Use when experience applying a skill reveals something its maintainers should
know: a failed command, misleading instruction, missing prerequisite, conflict,
feature request, or improvement supported by a concrete example. Report useful
feedback even when a workaround lets the main task continue.

## Actions

1. Identify the affected skill and the specific instruction or missing capability.
   Record the skills checkout revision (`git -C SKILLS_ROOT rev-parse HEAD`)
   and relevant local modifications. Distinguish skill defects from project
   bugs, environment failures, and an out-of-date deployed copy.
2. Search open and closed issues on `ligon/sucoder-skills` for the skill name
   and symptom. Read plausible matches. Add new evidence to an existing report
   when it covers the same problem; open a new issue for a distinct concern.
3. Write a concise title naming the skill and problem or proposed capability.
   Include the task context, expected and observed behavior, exact instruction
   or path, revision, reproduction or concrete example, and any workaround.
   For a feature request, explain the unmet use case and desired outcome.
   Mark hypotheses as hypotheses; do not claim a reproduction that was not run.
4. File with an explicit repository target. This guidance encourages agents to
   submit relevant feedback without a separate permission round trip when the
   session permits it. Honor instructions that restrict external writes; in
   that case prepare the report locally and explain that it remains unfiled.
   Exclude secrets and private project material; use a minimal sanitized example.
5. Record the resulting issue URL in the task handoff and resume the original
   task. Keep feedback proportionate; avoid speculative bulk reports or repeated
   comments that add no evidence. If filing fails, retain the draft and report
   the failure without claiming submission.

## GitHub commands

Use the connected GitHub tools when available, or `gh`. Replace the example
search term with the affected skill and search again for distinctive symptoms.

```bash
gh issue list --repo ligon/sucoder-skills --state all \
  --search '"skill-name"' --limit 100
gh issue view 123 --repo ligon/sucoder-skills --comments
```

A bounded search may omit older matches; refine the query when results reach
the limit. Write the exact issue body to a temporary file, then submit it:

```bash
gh issue create --repo ligon/sucoder-skills \
  --title 'skill-name: concise problem or request' --body-file /path/to/report.md
```

For additional evidence on an existing issue, use `gh issue comment` with
`--repo ligon/sucoder-skills` and `--body-file`. Avoid creating new labels merely
to file feedback. Check remote state before retrying an uncertain submission.

## Related skills

- [working-with-github](../working-with-github/SKILL.md): consult before writing
  issue-referencing commits or PRs, merging, or diagnosing inherited red CI.
- [document-skill](../document-skill/SKILL.md): use when implementing a skill change.

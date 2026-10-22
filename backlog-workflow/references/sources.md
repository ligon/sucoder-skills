# Source review and design rationale

Reviewed 2026-10-22. These are workflow precedents, not evidence that a ranking
formula or automation platform improves every project. Markdown matches this
repository's skill entrypoints and operational references.

## Local model

Source: `~/mirrors/LSMS_Library/.claude/skills/backlog-workflow/SKILL.md`,
especially "Phases", "Non-negotiables", and the 2026-10-14 residual-work rule.

Retain reconciliation before implementation, grouping by demonstrated root
cause, isolated fix worktrees, existing regression checks, and explicit
remaining work after partial fixes. Generalize cache handling to whether stored
artifacts can conceal the changed code.

Leave country tiers, Feature() audit commands, runtime details, and branch names
in LSMS. Make exploration a complete mode: the original primarily resolves
issues with multiple agents. Its closure and residual-filing steps become
proposals when the request only authorizes exploration. Preserve authorization
across steps rather than repeatedly seeking permission.

## Outside approaches

| Source | Useful approach | Adaptation |
|---|---|---|
| [Kubernetes issue triage](https://www.kubernetes.dev/docs/guide/issue-triage/) | Reproduce bugs, route ownership, distinguish accepted issues from those needing information; explicit lifecycle policy | Require evidence and next actions; retain local ownership and avoid importing stale-closure rules |
| [GitLab triage tutorial](https://docs.gitlab.com/tutorials/issue_triage/) | Define type, severity, and priority separately; organize labels and boards | Separate impact from scheduling; reuse project labels |
| [GitHub agentic issue triage](https://github.github.com/gh-aw/gallery/ai-issue-triage/) | Gather context and assess completeness, duplicates, and coding-agent readiness before constrained writes | Separate analysis from mutations; report readiness and confidence; keep the automation platform optional |
| [GitHub issue dependencies](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies) | Explicit blocking relationships | Order prerequisites first and expose cycles |
| [GitHub sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues) | Parent/child decomposition | Distinguish grouping from blocking and preserve parent acceptance criteria |
| [GitHub CLI issue list](https://cli.github.com/manual/gh_issue_list) | Bounded retrieval, default limit 30 | Make completeness explicit in the report |

Kubernetes and GitLab contribute maintainers' procedures. GitHub's agentic
example supplies an executable model for incoming reports. Backlog sweeps also
need historical reconciliation: reports may be partially implemented, duplicated,
reverted, or awaiting release. Combine these approaches with LSMS's residual
rule rather than equating incoming-issue classification with backlog management.

Avoid mandatory numerical scoring when impact and effort lack comparable units.
Prefer explained ordering with uncertainty. Avoid mandatory orchestration or a
new script layer until repeated use identifies steps worth automating. Revisit
these choices after real project sweeps.

# Collection and reporting

## Read-only collection

Set `repo` to a verified GitHub owner/name, not a mirror path. These examples
require authenticated `gh`; the first uses its built-in jq filtering.

```bash
repo=OWNER/REPO
gh repo view "$repo" --json nameWithOwner,defaultBranchRef,url
gh api --paginate "repos/$repo/issues?state=open&per_page=100" \
  --jq '.[] | select(has("pull_request") | not) | {number,title,html_url,updated_at,labels,assignees,milestone}'
```

The REST issues endpoint also returns PRs; the filter removes them. Output is a
stream of objects, not one JSON array. Save to a fresh snapshot file as needed.
Check exit status and disclose partial retrieval on failure. Counts may change
during pagination; record the collection interval and refresh candidates before
acting.

For a deliberately bounded sample:

```bash
gh issue list --repo "$repo" --state open --limit 100 \
  --json number,title,url,updatedAt,labels,assignees,milestone
```

This returns at most 100 issues, not proof of complete coverage. The default
limit is 30. Disclose filters and truncation.

```bash
issue=123
gh issue view "$issue" --repo "$repo" --comments
gh pr list --repo "$repo" --state all --search "#$issue" --limit 100 \
  --json number,title,url,state,baseRefName,mergedAt
```

Text search yields candidates, not an exhaustive graph of linked PRs. Inspect
timeline links, explicit dependencies, and relevant code history too. Follow
all pages for comments and timeline records when using REST. Disclose connector
truncation or inaccessible dependency metadata rather than reporting no links.

## Report fields

Keep the main table short and put evidence and residual drafts below it. Use
Org for saved reports when that is the project's convention.

| Field | Contents |
|---|---|
| Scope | Repository, mode, branches/SHAs, time, filters, budget |
| Coverage | Fetched, examined, unexamined, failures and limitations |
| Issue | Number, URL, title, last observed update |
| Assessment | Disposition, confidence, evidence links or code/test locations |
| Impact and order | Severity, urgency, effort range, priority rationale |
| Relationships | Duplicate, cluster, parent, blockers, active PRs |
| Next action | Concrete check/change, owner if known, completion criterion |
| Residual | Resolved subset and residual title/body for partial work |
| Action record | Proposed versus applied edits, result URLs, failed operations |

Count each examined issue once by its primary disposition, even when it belongs
to several clusters. Reconcile counts with coverage. Distinguish fetched
metadata from examined issues, and use "unknown" when evidence is missing.

## Walkthrough cases

- Exploration of 240 issues retrieves 100: disclose incomplete coverage and
  fetch the remainder if required by scope; do not publish tracker edits.
- A merged PR covers two of three criteria on a development branch: record
  partial work, branch status, and a residual draft; do not declare resolution.
- Similar titles concern different causes: retain both unless evidence
  demonstrates equivalent scope.
- A severe defect lacks data: rank its impact and give the missing-data action;
  do not quietly replace it with easy cosmetic work.
- A maintainer changes an issue after the snapshot: reconcile again before
  applying an authorized edit.
- A repeat sweep finds a residual issue and active PR: reuse their links and
  remaining scope; avoid duplicate work or comments.
- Tests pass while importing the base checkout: reject that result as patch
  verification and rerun against the intended worktree.

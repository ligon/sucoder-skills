# Handoff: resolve the skill-catalog / deployment issues on the cluster

**Audience:** an agent with Savio (cluster) access and the ability to modify the SuCoder source there. All repo pointers below are public; nothing here needs credentials beyond what the agent normally has.

## Background

Startup skill catalog bugs, tracked across two repos:

- `ligon/sucoder-skills` — skill definitions + the frontmatter lint.
- `ligon/sucoder` — the agent sandbox that builds the startup catalog.

Two skills (`workshop-problem`, `research-writer`) had an unquoted `: ` inside
their `description:` scalar, so PyYAML rejected their frontmatter and SuCoder's
catalog fell back to the literal entry name `SKILL` with no description — the
skills were undiscoverable at session start.

Current state:

- `ligon/sucoder-skills` PR #2 (merged): fixed both descriptions (`description: >-`) and added `scripts/lint_skills.py`.
- `ligon/sucoder-skills` PR #4 (open): wires `lint_skills.py` into `make check` / `make lint`. Merge it.
- `ligon/sucoder-skills` issue #3 (open): deployment/verification of the fix on local and Savio checkouts. The local-half was done; Savio half is the work below.
- `ligon/sucoder` issue #17 (open): fix the catalog fallback — on a failed frontmatter parse, fall back to the skill directory name and show a parse-error marker, not the literal `SKILL` stem.

## Work items

### 1. Resolve ligon/sucoder#17 (fallback fix, in the SuCoder codebase)

Find the catalog generator (the code that turns the skills directory into the
session-start catalog) and change the failed-parse path:

- fall back to the skill's **directory name** (e.g. `workshop-problem`), never
  the filename stem `SKILL`;
- mark the entry explicitly, e.g. `- <dir> — frontmatter failed to parse (load with ...)`.

The parse-error marker may partially exist already (referenced in sucoder-skills#3) —
verify against current SuCoder source at Savio rather than assuming.

Add a regression case alongside: feed a SKILL.md with a deliberately broken
frontmatter and assert the catalog entry carries the directory name and the
marker.

### 2. Update Savio's sucoder-skills checkout (closes the Savio side of #3)

Do NOT `git reset --hard` / `git clean` — preserve local commits, config, and
untracked files. Use this sequence per checkout:

```bash
git status --short --branch              # record baseline cleanliness
git rev-parse HEAD                        # record pre-update revision
git fetch https://github.com/ligon/sucoder-skills.git main
git merge --ff-only FETCH_HEAD            # if ff is impossible, stop and
                                          # merge/cherry-pick carefully instead
git rev-parse HEAD                        # record post-update revision
```

If the local `update` is blocked by real local commits, prefer
`git merge FETCH_HEAD` (a merge commit preserves history) over resetting.
Report the before/after revisions in a comment on issue #3.

### 3. Fix the remote on each checkout so plain `git pull` works (documented in the #3 comment)

The stale-update root cause was a remote pointing at a local-path clone
(`/home/ligon/Projects/sucoder-skills` in the local case). On Savio, check
`git remote -v`; if the fetch URL is not `https://github.com/ligon/sucoder-skills`,
repoint it:

```bash
git remote set-url origin https://github.com/ligon/sucoder-skills.git   # or whatever remote name is used
```

That makes step 2 collapsible to `git pull --ff-only` in future.

### 4. Merge PR #4 (lint gate), then run it on Savio

```bash
git fetch https://github.com/ligon/sucoder-skills.git main
make check            # or: python3 scripts/lint_skills.py
```

Expected: `31 SKILL.md checked, 0 problem(s)`. A nonzero report means bad
SKILL.md files remained — fix or flag instead of silencing the lint.

### 5. End-to-end validation through SuCoder's real startup path (closes #3 acceptance)

Run a SuCoder session on Savio (or whatever minimal entry point builds the
catalog) and confirm in its startup output/catalog/launch log that:

- `workshop-problem` and `research-writer` appear with names and full
  descriptions (659 and ~507 chars respectively);
- no literal `SKILL` entries and no parse-error markers remain;
- the checkout revision recorded in step 2 is the one consumed.

Careful: SuCoder may build the catalog from a skills checkout separate from
the one you updated in step 2 — trace the path it reads before claiming success.

### 6. Close out the issues

- Comment on `ligon/sucoder-skills#3` with: Savio before/after revision,
  remote-URL fix, lint output, and the end-to-end startup validation excerpt;
  close it once acceptance holds.
- Resolve `ligon/sucoder#17` with whatever PR/commit implements the
  directory-name fallback.

## Traps to avoid

- Do not silence the lint by excluding the broken files — success is the two
  descriptions being present, per issue #3's acceptance criteria.
- Do not claim validation from a PyYAML-only parse again (that was the local
  half of #3); SuCoder's own catalog path is the authority.
- Before merging PR #4, confirm Savio's environment has a `python3` with
  PyYAML for the lint script; if it doesn't, install or pin it in the Makefile.

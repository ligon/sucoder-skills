# Recovery Playbook

Decision tree for diagnosing and recovering from common broken states.

## Rule Zero: Diagnose Before Editing

When the working tree looks wrong, **never re-edit files to restore
missing content until you've confirmed it's actually missing**.
Rewriting correct content on top of stale working-tree state destroys
real changes.

The correct first action is always:

```bash
git status
git branch --show-current
git log --oneline -5
```

## Symptom: "Files I committed earlier are gone"

**Likely causes**:

1. You're on a different branch than you think
2. The working tree was reset to an earlier state
3. A different process (another agent, another session) checked out
   a different commit

**Diagnosis**:

```bash
git branch --show-current                   # which branch?
git log --oneline -5                         # what does this branch think it contains?
git log origin/<expected-branch> --oneline -5  # what does the remote have?
```

**If the remote is ahead of local**: fast-forward.

```bash
git fetch origin
git reset --hard origin/<branch>   # destructive; confirm first
```

**If the remote matches but you're on the wrong branch**: switch back.

```bash
git checkout <expected-branch>
```

**If the remote is ALSO missing the commits**: they never made it
anywhere.  Check `git reflog` for the original commit hashes:

```bash
git reflog                  # shows HEAD movements
git show <hash>             # verify it's the expected commit
git cherry-pick <hash>      # or git reset --hard <hash>
```

## Symptom: "Working tree has modifications I didn't make"

**Likely causes**:

1. An agent wrote to the main tree instead of its worktree
2. A linter or format hook modified files
3. A different session ran a partial command

**Diagnosis**:

```bash
git diff                           # see what changed
git status -sb                     # concise overview
git log -p --since="1 hour ago"    # recent commits
```

**If the changes are unwanted**:

```bash
git checkout -- <file>             # discard for a single file
git checkout -- .                  # discard everything (destructive)
git restore <file>                 # same, newer syntax
```

**If the changes might be valuable**:

```bash
git stash                          # save for later review
git stash show -p stash@{0}        # inspect the stash
git stash drop stash@{0}           # if not needed
```

## Symptom: "An agent wrote to main tree instead of worktree"

This can happen if a worktree agent has the wrong working directory,
or if path resolution fails and the agent falls back to the main
repo path.

**Diagnosis**:

```bash
git status                         # uncommitted changes on main tree
git worktree list                  # active worktrees
```

**Recovery**:

1. If the worktree is still running, kill it: find the worktree
   directory under `.claude/worktrees/` and `git worktree remove
   --force`
2. Stash or commit the modifications on the main tree
3. Decide whether to keep them (the agent did useful work) or discard
   them (the agent went off-script)
4. Re-dispatch in a fresh worktree with clearer path constraints in
   the prompt

## Symptom: "Stale `.claude/worktrees/` directories"

**Diagnosis**:

```bash
git worktree list                  # active worktrees
ls .claude/worktrees/              # directories on disk
```

If there are directories without corresponding worktree entries, they
are stale.

**Cleanup**:

```bash
git worktree prune                 # removes invalid entries
rm -rf .claude/worktrees/agent-XXX # for orphaned directories
git branch -D worktree-agent-XXX   # any leftover branches
```

## Symptom: "DVC lock contention"

**Error**: "Unable to acquire lock" or similar from `dvc` commands.

**Diagnosis**:

```bash
ps aux | grep dvc                  # is a dvc process still running?
ls lsms_library/countries/.dvc/tmp/lock*   # stale lock files?
```

**Recovery**:

- **If a dvc process is running**: wait for it, or kill it cleanly
- **If no dvc process**: remove the stale lock files
  ```bash
  rm lsms_library/countries/.dvc/tmp/lock*
  ```
- **Prevention**: use `LSMS_BUILD_BACKEND=make` (or project
  equivalent) to bypass DVC during parallel agent runs

## Symptom: "Agent appears stuck / not making progress"

**Diagnosis**: Check the agent's output file for recent activity:

```bash
wc -l /tmp/.../tasks/<agent-id>.output     # is the line count growing?
tail -20 /tmp/.../tasks/<agent-id>.output  # what was it last doing?
ps aux | grep <agent-id>                    # is the process alive?
```

**Decision**:

- **Making slow progress** (lines/min > 0): let it finish, but set a
  mental timebox
- **Stalled** (no new lines for >2 minutes): the agent is rabbit-holing
  or hung.  Kill it
- **Alive but doing the wrong thing**: kill it, redirect with a
  clearer prompt

**Kill the agent**:

```bash
# If dispatched via Agent tool, there may be no direct kill.
# Kill the process and clean up the worktree:
pkill -f "<agent-id>"
git worktree remove .claude/worktrees/agent-<id> --force
git branch -D worktree-agent-<id>
```

## Symptom: "Tests fail after a clean cache rebuild"

**Diagnosis**:

1. Are the failures in structural tests (schema, paths, imports)?
   → Real code problem, not a cache issue.
2. Are the failures in data-building tests (invariance baselines,
   country-level builds)?  → Likely the clean cache is missing
   something the tests need.  Check whether the source data is
   accessible (DVC pull, WB authentication).
3. Are the failures specific to a few tables?  → Look at the
   wave-level scripts for those tables; they may write `v` or other
   fields that conflict with the current API-time joins.

**Recovery**:

- If the failures are data-access related: ensure DVC/WB credentials
  are in place, or run with `LSMS_SKIP_AUTH=1` and accept that some
  tests will skip
- If the failures are structural: they're real bugs — investigate
  directly, don't delegate until you understand the scope

## Symptom: "Subagent didn't inherit workspace skills"

Subagents don't see `.claude/skills/` automatically.  They see only
what's in their prompt.

**Fix the prompt**, not the skills directory:

```
Before starting, read the skill at:
.claude/skills/add-feature/SKILL.md

Then complete the task: {task description}
```

Be explicit about which skills to load.  Subagents cannot discover
skills the way the top-level session can.

## Symptom: "Local branch is behind remote after a reset"

**Situation**: `git reset --hard HEAD` (or similar) was run while the
branch was behind the remote.  Local now shows older commits as HEAD.

**Diagnosis**:

```bash
git status                         # says "behind origin by N commits"
git log origin/<branch> --oneline -5   # shows the commits you're missing
```

**Recovery**:

```bash
git reset --hard origin/<branch>
```

This is safe because the remote is authoritative.

## General Principle

When in doubt, **consult the remote**.  `origin` is the source of
truth for anything that has been pushed.  Local state can be
corrupted, reset, or made inconsistent by various processes, but the
remote is stable.

The recovery flow is almost always:

1. `git fetch origin`
2. Check `git log origin/<branch>` to see what the remote believes
3. Decide whether to fast-forward, reset, or cherry-pick
4. Execute
5. Verify by checking a key file's content against what you expected

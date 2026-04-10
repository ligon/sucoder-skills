# Dispatch Patterns

Worked examples of common scrum-master dispatches.  Each pattern
shows the situation, the prompt shape, and things to watch for.

## Pattern 1: Parallel Country/File Sweep

**Situation**: A single mechanical change applies to N independent
items (countries, data files, feature configs).  Each item is small
but the aggregate would take too long to do sequentially.

**Approach**: Dispatch N agents in a single message, one per item.
All launch in parallel.  Collect notifications as they arrive.

**Prompt shape** (per agent):

```
You are fixing {item} as part of a larger sweep.  The change needed:
{specific edit description}.

Files to modify:
- path/to/file1
- path/to/file2

Constraints:
- Do NOT touch files outside this list
- Do NOT commit; the scrum master commits after review
- Verify YAML/JSON parses after each edit
- Report under 100 words
```

**When to prefer a single script instead**: If the change is truly
uniform (regex replacement, same dict transformation everywhere), a
for-loop script is faster and more auditable than N agents.  Use
agents when per-item judgment is needed (e.g., the variable names
differ across countries).

## Pattern 2: Worktree Experiment

**Situation**: Attempting a potentially-destructive or speculative
change that may need to be abandoned.  Don't want it touching the
main checkout.

**Approach**: Dispatch a worktree agent.  It works on a snapshot
branch; the scrum master reviews before merging.

**Prompt shape**:

```
Attempt to {objective} on a worktree.  Context: {why this matters}.

Specific changes to try:
1. {step 1}
2. {step 2}

Constraints:
- Do NOT commit to master/development from the worktree
- Do NOT modify files outside {scope}
- Report: what worked, what didn't, diff of changed files
```

**Watch for**:
- Credentials: decrypted cred files may not be in the worktree;
  copy them if the agent needs them
- Stale snapshots: the worktree sees the branch as of dispatch time,
  not later commits
- Cleanup: after merging or abandoning, `git worktree remove
  --force` and `git branch -D`

## Pattern 3: Well-Defined Fix with Known Recipe

**Situation**: A previous investigation (or a user's explicit
direction) produced an exact recipe.  The scrum master just needs the
mechanical work done.

**Approach**: Foreground or background agent with the recipe
copy-pasted into the prompt.

**Prompt shape**:

```
Apply the following fix to tests/test_dvc_caching.py.  A previous
agent diagnosed the root causes — here is the exact recipe:

1. Add `monkeypatch` fixture parameter to these 4 tests:
   {list of test names}
2. Add `monkeypatch.setenv("LSMS_BUILD_BACKEND", "dvc")` at the top
   of each.
3. Add these two patches to each test's `with patch(...)` block:
   - patch("lsms_library.country._load_canonical_spellings", return_value={})
   - patch("lsms_library.country._load_rejected_column_spellings", return_value={})

Verify by running: {exact pytest command}

Report: pass/fail for each test.
```

**Why the recipe format works**: the agent doesn't need to discover
anything.  It just executes.  Fast, reliable, reviewable.

## Pattern 4: Investigation Agent

**Situation**: Need to know something about the codebase before
deciding what to do.  The scrum master shouldn't burn their own
context reading files.

**Approach**: Explore agent (if available) or general agent with a
short, scoped prompt.

**Prompt shape**:

```
Survey the codebase for {specific thing}.

Look in:
- {directory or pattern}
- {directory or pattern}

For each finding, report:
- File path and line number
- Brief description of what it does
- Why it matches the criteria

Report under 300 words.  Do NOT make any changes.
```

**Key rule**: An investigation agent should NEVER modify files.  If
the scrum master wants changes based on the investigation, that's a
separate second dispatch with a different agent and a narrower prompt.

## Pattern 5: Second-Opinion Review

**Situation**: The scrum master has made or reviewed a change and
wants an independent read before landing it.

**Approach**: Dispatch a reviewer agent that **doesn't see the
reasoning**, just the diff.  This catches things the original
reviewer rationalized.

**Prompt shape**:

```
Independent review of {file or diff}.  Context: {one paragraph
about what the change does}.

Specifically evaluate:
- {question 1}
- {question 2}

Give a frank assessment.  If the change looks wrong, say so; if it
looks fine, say so.  Do NOT rubberstamp.  Report under 200 words.
```

**Anti-pattern**: Telling the reviewer what you concluded before
asking them.  That primes them to agree.

## Pattern 6: Long-Running Background Task

**Situation**: A full test run, cache rebuild, or data build that will
take minutes-to-hours.  The scrum master shouldn't wait.

**Approach**: Background command via `run_in_background: true`.  The
scrum master keeps working and is notified on completion.

**Prompt shape** (for Bash tool, not Agent):

```bash
LSMS_SKIP_AUTH=1 .venv/bin/python -m pytest tests/test_feature.py -v 2>&1
```

Run with `run_in_background: true`.  Review output when notified.

**Watch for**:
- Don't re-poll the output file in a loop; you'll be notified
- Don't sleep waiting for it; do something useful instead
- If the test suite is known to trigger expensive rebuilds, consider
  whether to clear caches first or select a narrower subset

## Pattern 7: Scatter-Gather with Re-Dispatch

**Situation**: Running a parallel sweep where some items may fail.
Want to collect successes, re-dispatch failures with more context.

**Approach**:

1. First pass: dispatch N agents, one per item, all in parallel
2. As notifications arrive, commit each success to a shared branch
3. Collect failures with their error messages
4. Second pass: dispatch new agents for just the failures, including
   the specific error and any context that would help (e.g., "the
   first attempt failed with X; check whether Y is the root cause")
5. Iterate until all items succeed or reach a hard blocker

**Commit cadence**: Commit each success immediately.  Don't wait for
the whole sweep to finish.  If something goes wrong, the committed
work is safe.

## Pattern 8: Bidirectional Message Channel

**Situation**: A long-running agent (minutes to hours) where the
scrum master might need to redirect it mid-flight, or the agent
might hit a question that needs human judgment.

**Approach**: Provision two files **before dispatching** and tell
the agent about them in the prompt.

**Setup** (before dispatch):

```bash
CHANNEL=slurm_logs/build_$(date +%Y-%m-%d)
mkdir -p "$CHANNEL"
: > "$CHANNEL/MESSAGES_TO_AGENT.txt"
: > "$CHANNEL/QUESTIONS_FROM_AGENT.txt"
```

**Prompt shape**:

```
{task description}

## Bidirectional message channel

This task may take a while.  Steering and blocking questions flow
through two files:

- `slurm_logs/build_2026-04-10/MESSAGES_TO_AGENT.txt` — at the top
  of each major step, re-read this file.  If it has new lines
  compared to what you saw previously, follow the new instructions.
  The scrum master uses this to redirect, cancel, or answer
  questions.

- `slurm_logs/build_2026-04-10/QUESTIONS_FROM_AGENT.txt` — if you
  hit a blocking question or need clarification, append a dated
  question (e.g., `2026-04-10 14:23 Q: ...`) and proceed with the
  next independent sub-task while waiting.  Do not block entirely.
  Do not ask the same question twice.

Do NOT assume questions will be answered immediately.
```

**Monitoring from the scrum master side**:

```bash
# Periodically check for questions
tail -f slurm_logs/build_2026-04-10/QUESTIONS_FROM_AGENT.txt

# Send a steering message
echo "2026-04-10 14:25 A: for Tanzania 2008-15, use the round column, not filename" \
  >> slurm_logs/build_2026-04-10/MESSAGES_TO_AGENT.txt
```

**When this pattern shines**:

- **Scatter-gather with shared channel**: All N agents in a sweep
  read the same `MESSAGES_TO_AGENT.txt`, so one append broadcasts to
  all of them ("stop — the framework has a bug, don't proceed")
- **Cross-cutting questions**: If 3 of 10 agents ask the same
  question, the scrum master spots the pattern and writes one answer
  that all three (and future agents) will see
- **Reclaiming a runaway agent**: "2026-04-10 14:30: Stop further
  file edits.  Summarize what you've done and exit."

**Anti-pattern**: Expecting the agent to poll the channel at sub-second
intervals.  The agent re-reads at checkpoints it chooses; the scrum
master's timing guarantees are loose (seconds to a minute).  This is
an async channel, not a synchronous control pipe.

**Cleanup**: After the session, archive or delete the session
directory.  Stale message files from yesterday should not contaminate
today's dispatches.

## Pattern 9: Agent-as-Coordinator (rare)

**Situation**: A multi-step workflow with conditional branching that
would be tedious for the scrum master to babysit.

**Approach**: Dispatch a single coordinator agent with enough
context to make the branching decisions itself.

**When to use**: Rarely.  The scrum master should generally retain
coordination authority.  Use this only for workflows the user has
explicitly asked to be "fully handled" and where the decisions are
low-stakes.

**Watch for**: Coordinator agents tend to rabbit-hole.  Set a strict
time limit or dispatch count limit in the prompt.

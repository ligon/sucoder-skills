---
name: scrum-master-hpc
description: Use this skill when acting as a scrum master / dispatcher on an HPC login or compute node with Slurm access and multiple agent tools. This skill should be used to stay lightweight, delegate work safely to subagents (local or Slurm-dispatched), maintain branch and cache discipline, and recover cleanly when the working tree looks wrong. It trips on user cues like "be the scrum master", "delegate this", "dispatch agents", or when the user mentions managing many parallel tasks across countries/features/files.
---

# Scrum Master on an HPC Node

## Overview

This skill codifies the norms for playing project manager on a shared HPC
node (e.g. Savio, NERSC) where a Slurm scheduler, multiple cores, and
sibling compute nodes are available.  The core idea: stay lean and
interactive, push compute-heavy or mechanical work to subagents, and
keep the repository state legible for humans who'll read the git log
tomorrow.

The role is distinct from a worker agent.  A scrum master:

- **Decides what to delegate** and what to do directly
- **Dispatches** agents (locally, in worktrees, or via Slurm) and
  **reviews** their output before it lands on a shared branch
- **Maintains branch, cache, and worktree hygiene** so the next session
  (human or agent) starts from a clean state
- **Recovers gracefully** when something looks wrong (a stale worktree,
  a reset branch, a dead agent)

Everything below assumes the repository already follows the patterns in
its own `CLAUDE.md` — this skill is about the meta-concerns of working
above it.

## Quick Start

At the start of a scrum-master session, run this checklist:

1. **Know where you are**: `git status` and `git branch --show-current`.
   Never assume.
2. **Know what compute you have**: `nproc`, `free -h`, `uname -n`, and
   `sinfo` for the cluster you're on.  See the [Slurm reference](references/slurm_dispatch.md)
   for partition-picking guidance.
3. **Know what's running**: `squeue -u $USER` for your Slurm jobs.
4. **Check for stale state**: leftover worktrees under
   `.claude/worktrees/`, stale DVC locks, half-finished branches.
5. **Confirm today's date**: `date`, since handoff notes use it.

Do not start dispatching until the above is clear.

## Core Principle: Stay in a Fit State

The scrum master's job is to stay **interactive and responsive**.  Every
compute cycle spent reading large output, building parquets, or grinding
through mechanical edits is a cycle not spent on judgment calls the user
needs you for.  The rule of thumb:

> If it can be written as a clear one-paragraph prompt to another agent,
> delegate it.  If it requires judgment about project direction, design
> trade-offs, or "is this safe?", do it yourself.

This doesn't mean "delegate everything".  It means **delegate
understanding-free tasks** and keep the judgment calls in your own
context.

## When to Delegate vs. Do It Directly

| Task shape | Delegate? | Notes |
|---|---|---|
| Full test run, long build, multi-country sweep | ✅ Yes | Background or Slurm; pure compute |
| Well-defined fix with known recipe | ✅ Yes | Pass the recipe in the prompt; review the diff |
| Mechanical edit across many files with a clear pattern | ✅ Yes | One agent for a batch, or one per file if complex |
| Investigation: "find all the places that X" | ✅ Yes | Explore agent or general agent |
| Second-opinion review of a design or diff | ✅ Yes | Independent review = fresh eyes |
| Architectural change touching the heart of the codebase | ❌ No | Review personally; maybe have an agent draft in a worktree |
| Prioritization / which bug matters most | ❌ No | Judgment call |
| Merges into main/development | ❌ No | You control the branch |
| Changes to test expectations / baselines | ❌ No | Design decision, not mechanical |
| Anything the user would want to see immediately | ❌ No | Keep it in your own hands |

When in doubt, **delegate the search but not the synthesis**.  An agent
can produce a list of candidate files; the scrum master decides which
matter.

## Dispatch Modes

Four ways to dispatch work, in increasing order of isolation:

### 1. Foreground agent (in-process)

Use the Agent tool without `run_in_background`.  Blocks the scrum master
until the agent finishes.  Appropriate when the agent's output is
needed to decide the next step.

### 2. Background agent (in-process)

Use the Agent tool with `run_in_background: true`.  The scrum master
keeps working and gets notified on completion.  Appropriate when the
agent's work is independent of whatever comes next.

### 3. Worktree agent (isolated)

Use the Agent tool with `isolation: "worktree"`.  The agent operates on
a git worktree snapshot of the repo, so its changes don't touch the
main checkout.  Appropriate when the agent might modify files the
scrum master is also touching, or when trying a potentially-destructive
approach that may need to be abandoned.

Worktree pitfalls:
- **Stale snapshots**: The worktree is created from the branch tip at
  dispatch time.  If the scrum master commits a fix after dispatching,
  the worktree doesn't see it.  Either commit first, or don't use a
  worktree for tasks that depend on recent changes.
- **Credential propagation**: Decrypted credentials (e.g.,
  `.dvc/s3_creds`) may be `.gitignore`d and not present in the
  worktree.  Copy them explicitly if the agent needs them.
- **Cleanup**: Remove worktrees and their branches promptly after
  merging.  Stale worktrees confuse git operations.

### 4. Slurm job (separate node)

Submit a job to another node via `sbatch`.  Appropriate for expensive
compute that shouldn't run on the login/current node, or when
parallelism exceeds the current node's cores.  See
[references/slurm_dispatch.md](references/slurm_dispatch.md) for a
ready-to-use submission template.

## Parallel Orchestration (Scatter-Gather)

When the same task applies to many independent items (countries,
files, features), **dispatch one agent per item in a single message**.
All agents launch in parallel.  The scrum master collects notifications
as they arrive, reviews each, commits successes, re-dispatches failures
with more context.

**Anti-pattern**: batching N items into one agent that processes them
sequentially.  That uses one core while N-1 sit idle.

**Rule of thumb**: prefer N agents doing 1 item each over 1 agent
doing N items.  The exception is when N is very small (2-3) and each
item is very cheap.

For the mechanical-cleanup case (e.g., "remove `v` from 30
data_scheme.yml files"), a **single script** (written and run directly
by the scrum master) is often better than 30 agents.  Agents add
latency and context-load; a for-loop is instant.

## Branch Hygiene

- **Commit early, commit often.**  The default is to commit each
  meaningful unit of work as soon as it's tested.  A session that
  accumulates uncommitted changes is fragile.
- **Push after committing.**  The working tree can vanish (another
  process, another session); `origin` is the source of truth.
- **Active development goes on a `development` branch.**  Never commit
  speculative work directly to `master`/`main`.  Merge to master only
  when confident and when coverage is complete.
- **Prefer fast-forward merges** to keep history linear.
- **Co-author trailer**: When an LLM agent wrote significant portions
  of the commit, include a `Co-Authored-By:` trailer identifying the
  model so humans can distinguish automated contributions.

## Worktree and Branch Cleanup

After a worktree agent's work is merged (or deliberately abandoned):

```bash
git worktree remove .claude/worktrees/agent-XXXXX --force
git branch -D worktree-agent-XXXXX
```

Run `git worktree list` periodically to catch leftovers.  A stale
worktree whose agent has stopped still counts against `git worktree`
operations and can cause confusing errors.

## Cache Discipline

HPC projects often have a large on-disk cache (parquets, intermediate
artifacts).  When the cache might contain stale content:

1. **Clear before full rebuilds** if a structural change would
   invalidate cached data.
2. **Trust the cache when reading-only**, but use `trust_cache=False`
   (or the project equivalent) when diagnosing data quality.
3. **Be careful what you run with a clean cache.**  A test suite that
   triggers data builds can consume hours of CPU on a cleared cache;
   prefer structural tests first, data tests second.
4. **Stale parquets during regression comparison are a trap.**  If
   you are comparing outputs between two versions of the code (e.g.
   old branch vs. new branch), and either side has cached parquets
   from a previous build, the "difference" you observe may reflect
   old-code-cached-output versus whatever the other side is currently
   producing — not the real behavioral delta between the two code
   versions.  Always clear the caches on both sides before the
   comparison, or rebuild the side under test before comparing.  A
   dispatched regression agent that reports "schema difference"
   should be asked to verify by rebuilding at least one
   representative table from source on the side under test.

## State Recovery

When the working tree looks wrong (files revert to an older state,
branch is on the wrong name, etc.), the correct first action is **not**
to panic or start re-editing.  Instead:

1. `git status` to see the claimed state
2. `git branch --show-current` to confirm which branch
3. `git log --oneline -5` on the current branch
4. `git log origin/<branch> --oneline -5` to see the remote
5. If local is behind remote: `git fetch origin && git reset --hard origin/<branch>`
6. If the working tree has uncommitted changes matching an older commit:
   you may have been checked out on a different branch.  Switch back.
7. Verify the expected files contain the expected content before
   continuing.

**Never re-edit files to "fix" what looks like a missing change until
you've confirmed it's actually missing.**  Rewriting correct content
on top of incorrect working-tree state destroys the real change.

## Message Discipline with Subagents

Prompts to agents are **self-contained**.  They don't see the scrum
master's conversation history.  Every prompt should:

- State the task in one sentence at the top
- Explain what the agent already needs to know (file paths, prior
  commits, why the task matters)
- List the concrete steps or criteria for completion
- State explicitly what NOT to do (don't commit, don't touch X,
  don't modify other files)
- Request a short report on completion if the agent is for
  investigation (under 200 words)

**Never write "based on your findings, fix the bug"** or "based on the
research, implement it" — that pushes synthesis onto the agent.
Instead, run the investigation, read the report, then issue a second
prompt with the specific change to make.

### Bidirectional message channel for long-running agents

For agents expected to run more than a few minutes, set up two files
**before dispatching** and pass their paths in the prompt:

- **`MESSAGES_TO_AGENT.txt`** — the scrum master appends steering
  notes, answers, or "stop doing that" mid-flight.  The agent
  re-reads it at natural checkpoints.
- **`QUESTIONS_FROM_AGENT.txt`** — the agent appends questions or
  blockers.  The scrum master polls it periodically (or the user
  prompts a check).

**Create the files before dispatch, do not tell the agent to create
them.**  Telling the agent "create it if missing" shifts a
setup-time decision to the agent's runtime, and a distracted or
rushed agent may skip creation entirely, silently disabling the
channel.  Two one-line commands before the dispatch:

```bash
: > slurm_logs/build_$(date +%Y-%m-%d)/MESSAGES_TO_AGENT.txt
: > slurm_logs/build_$(date +%Y-%m-%d)/QUESTIONS_FROM_AGENT.txt
```

Then include instructions like this in the prompt:

```
You may receive steering during this task.  At the top of each
major step, re-read:
  slurm_logs/build_YYYY-MM-DD/MESSAGES_TO_AGENT.txt
(the file already exists; it may be empty or contain new directives)

If you have a blocking question or need clarification, append it to:
  slurm_logs/build_YYYY-MM-DD/QUESTIONS_FROM_AGENT.txt
(the file already exists) and proceed with the next independent
sub-task while waiting for an answer (do not block).  Do not ask
the same question twice.
```

This turns a one-shot fire-and-forget dispatch into something closer
to a brief collaboration.  It's especially valuable for scatter-gather
sweeps where a single `MESSAGES_TO_AGENT.txt` can broadcast to all
agents at once ("stop on failure — config change needed"), and the
coordinator can read aggregated `QUESTIONS_FROM_AGENT.txt` to spot
cross-cutting problems.

Keep the files in a session-specific directory (e.g.,
`slurm_logs/build_2026-04-10/`) so old channels don't contaminate
new sessions.

## Recording the Session

For long or complex sessions, keep a running handoff note (an org or
markdown file in `slurm_logs/` or equivalent).  Record:

- Date and brief session summary
- What was committed (hash + one-line description)
- What agents were dispatched and what they did
- Open questions / half-finished work
- Known issues surfaced during the session

This is the "context transfer" for the next scrum master (or the same
one tomorrow).

## Resources

- **[references/slurm_dispatch.md](references/slurm_dispatch.md)** —
  Partition selection, job submission template, monitoring, and
  preemption handling for compute-heavy dispatch.
- **[references/dispatch_patterns.md](references/dispatch_patterns.md)** —
  Worked examples of common scrum-master dispatches: parallel sweeps,
  worktree experiments, batch edits, investigation agents, second
  opinions.
- **[references/recovery_playbook.md](references/recovery_playbook.md)** —
  Decision tree for diagnosing and recovering from common broken
  states: wrong branch, stale worktree, DVC lock contention, agent
  overwriting committed changes.

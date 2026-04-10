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
4. **Know your budget**: run the cluster's account-usage tool (on
   Savio, `check_usage.sh -a <priority_account>`) and record the
   remaining balance in the session handoff.  See the
   [Cost Awareness](#cost-awareness) section.
5. **Check for stale state**: leftover worktrees under
   `.claude/worktrees/`, stale DVC locks, half-finished branches.
6. **Confirm today's date**: `date`, since handoff notes use it.

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

## Cost Awareness

Compute has two costs, and the scrum master is responsible for both:

1. **Private cost** — Service Units (SUs) drawn from your PI's
   allocation, billed to a fair-share or condo account (e.g.
   `fc_jevons` on Savio).  Denominated in SUs, not CPU-hours, because
   partition multipliers apply: newer hardware charges more SUs per
   wall-hour than older.  **Think in SUs.**
2. **Social cost** — queue delay and blocked capacity for every other
   researcher sharing the cluster.  This is the cost *you* don't pay
   but *they* do.  On whole-node partitions, a 55-minute
   single-threaded pytest on a 56-core HTC node is effectively a
   51-core-hour gift to nobody — a gift that, had the node been
   released, would have shortened someone else's queue wait.

The second cost is frequently larger than the first.  A group with
deep allocation headroom might pay nothing meaningful for 50 wasted
core-hours, but the graduate student whose experiment waited 45
minutes behind your job paid 45 minutes of their life.  Marginal
private cost and marginal social cost can point in opposite
directions.

### The rule: minimize the sum

When the two costs point in the same direction, the answer is
obvious.  When they diverge, **lean social**:

- Single-threaded on a whole-node partition: low private cost, high
  social cost → parallelize or resize.
- `fc_jevons` when `co_carleton` would work: nonzero private cost,
  low social cost (allocation has slack) → use `co_carleton`.
- A 2-minute job on any account: negligible both ways → don't
  over-think it.

Even if your group's allocation is effectively infinite, **other
researchers share the queue**.  If you wouldn't be comfortable
explaining the resource use to the person whose job was delayed
behind yours, don't dispatch it that way.

### Knowing the numbers

Savio-specific (generalize to your cluster):

```bash
# Account balance: how much of the priority allocation is left?
check_usage.sh -a <priority_account>           # e.g. fc_jevons

# Your personal usage this allocation year
check_usage.sh -u $USER

# Fair-share position (useful for diagnosing queue waits)
sshare -A <priority_account> --all

# Period utilization with per-user breakdown
sreport -t hours cluster accountutilizationbyuser \
    start=$(date -d '1 month ago' +%Y-%m-%d) end=now account=<priority_account>
```

`check_usage.sh` lives at `/global/home/groups/allhands/bin/` on
Savio and is on `$PATH` by default.  The key number is SUs consumed
vs. SUs allocated; treat >80% as a warning threshold worth
surfacing to the human.

### Protocol for the scrum master

1. **At session start**, run the account-usage command as part of
   the Quick Start checklist.  Record the remaining SU balance in the
   session handoff.  If usage is above ~80% of allocation, surface it
   immediately: switch all non-urgent work to the free account and
   flag the situation to the human.

2. **Before submitting any large job** (wall ≥ 2h, or whole-node
   allocation) on a billed account, estimate SU cost and report it
   in the dispatch message.  Rough formula:

       SUs ≈ cores × wall_hours × partition_multiplier

   Multipliers vary by cluster; for Savio, dividing the `sreport`
   SUs by the CPU-hours for the same period gives an empirical
   blended rate per partition.

3. **At session end**, re-run the account-usage command and record
   the delta in the handoff note.  That delta is the session's bill.

4. **On whole-node partitions, saturate or resize** — never block a
   big node with a single-threaded job.  See "Whole-Node Allocation"
   in `references/slurm_dispatch.md`.

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

Three standing rules when dispatching to Slurm:

- **Default to the free, low-priority account.**  Priority / condo
  accounts (e.g. `fc_jevons`) draw down shared compute budget and
  should be reserved for urgent work.  Free low-prio accounts (e.g.
  `co_carleton` on Savio) cost nothing and handle most workloads
  fine.  Ask before billing a priority account.
- **Ask modestly, saturate what you're given.**  Request a
  schedulable core count and memory (e.g. `--cpus-per-task=8`,
  `--mem=32G`) — enough for the work, schedulable on most nodes,
  recoverable after preemption.  Inside the job, read
  `$SLURM_CPUS_ON_NODE` to detect what Slurm actually handed you,
  and saturate that with `pytest -n $NPROC`, `make -j$NPROC`, etc.
  On most shared partitions the runtime figure equals the request;
  on the rarer whole-node partitions it may be larger.  Either way
  the same code works.  **Never use `pytest -n auto`** inside a
  cgroup-limited Slurm job — `os.cpu_count()` reports the physical
  node count, not the cgroup-restricted count, and you'll
  oversubscribe by N×.  **Never hard-code a big core count** in
  the `sbatch` line just to grab "bonus" cores — it locks you out
  of smaller hardware and most lower-priority partitions.
- **Scale out, not up.**  If the work genuinely needs more cores
  than a modest single-node ask gives, the right move is
  `--nodes=N` (or an array job), not hunting for one massive node.
  Horizontal scale is friendlier to the scheduler, fits on more
  partitions, and degrades gracefully under preemption — a
  preempted element of an array job costs one element's work,
  not the whole job.

All three rules are expanded in
[references/slurm_dispatch.md](references/slurm_dispatch.md).

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

Bidirectional steering of long-running agents is covered in the
[Monitoring Long-Running Work](#monitoring-long-running-work)
section below, alongside the distinct pattern for Slurm jobs.

## Monitoring Long-Running Work

Any dispatch longer than a few minutes needs observability.  Without
it, the scrum master either polls anxiously (wasting context on raw
log output) or forgets the job entirely (wasting compute and
delaying results).  How you observe depends on whether the
dispatched target is an **LLM agent** that can read steering files
at checkpoints, or a **deterministic process** like a Slurm job
running pytest, make, or a plain Python script.

| | LLM agent | Slurm job / deterministic script |
|---|---|---|
| Target reads files at checkpoints? | Yes | No |
| Mechanism | Bidirectional file channel | One-way filtered log stream |
| Tool | Plain files + the agent's own Read tool | `Monitor` harness tool + `tail -F` |
| Control | Append to `MESSAGES_TO_AGENT.txt` | `scancel JOBID` (binary) |
| Completion signal | Agent writes a final report | `sacct -j JOBID --format=State` |

Pick the right pattern for the target.  Do not try to use the agent
pattern for Slurm jobs — a pytest subprocess cannot re-read a
steering file.

### LLM agents: bidirectional file channels

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

### Slurm jobs: one-way filtered Monitor

A Slurm job is a deterministic process — pytest, make, a Python
script — that cannot read steering files.  Observability is
one-way, from the job's logs to the scrum master.  The right tool
is the harness's **`Monitor`**, which streams filtered stdout from a
background shell script into the chat as notifications.

**Attach Monitor at dispatch time, not later.**  Polling `squeue`
and `tail`-ing logs by hand means you waste context reading raw
output and only notice problems when you think to look.  Monitor
pushes the signal to you: matching log lines become notifications,
and you keep working until something matters.

**The filter is the whole discipline.**  Every stdout line from the
Monitor command becomes a chat notification, so you must emit only
the lines that carry signal.  Raw `tail -f` on a pytest log is a
flood — every PASSED line, every progress percentage, every
`make[1]: Entering directory` — and the harness will auto-stop an
over-producing monitor.  Design the filter around failure signals
and summary lines, never progress.

Reference implementation for a pytest Slurm job:

```bash
LOG=slurm_logs/session/pytest_${JOBID}.out
JOBID=33329846

echo "=== monitor attached $(date +%H:%M:%S) jobid=$JOBID ==="

# Catch-up: emit any past failures/errors/summaries already in the log
grep -E 'FAILED \[|ERROR \[|short test summary info|[0-9]+ passed' \
    "$LOG" 2>/dev/null | tail -40

# Live stream: only lines that carry signal
tail -n 0 -F "$LOG" 2>/dev/null | \
  grep --line-buffered -E \
    'FAILED \[|ERROR \[|short test summary info|[0-9]+ passed.*[0-9]+ (failed|error)|^FAILED |^ERROR ' &
TAIL_PID=$!

# Poll Slurm for job completion every 30s
while true; do
    state=$(sacct -j $JOBID --format=State --noheader --parsable2 \
              2>/dev/null | head -1 | tr -d ' ')
    case "$state" in
        COMPLETED|FAILED|CANCELLED*|TIMEOUT|NODE_FAIL|OUT_OF_MEMORY)
            sleep 5  # let the log flush
            echo "=== JOB $JOBID EXITED STATE=$state $(date +%H:%M:%S) ==="
            tail -5 "$LOG" 2>/dev/null
            kill "$TAIL_PID" 2>/dev/null
            exit 0
            ;;
    esac
    sleep 30
done
```

Dispatch this with `Monitor(persistent=true, ...)` so the watch
survives for the whole job.  When Slurm reports a terminal state,
the script emits one final marker line, tails a few lines for
immediate context, and self-terminates.

**Filter design principles:**

- **Emit only signal.**  For pytest: `FAILED [`, `ERROR [`,
  `short test summary info`, and the blended-count summary
  (`257 passed, 6 failed, 50 skipped`).  For `make`:
  `^make.*Error`, `^Error:`, and an explicit completion marker
  you echo yourself.
- **Always use `grep --line-buffered`** inside pipes.  Without it,
  pipe buffering delays events by minutes, and the job-exit
  notification can land before the failure notifications.
- **Catch up on attach.**  A plain `grep` over the existing log
  before starting the live `tail -F` picks up any failures that
  happened between dispatch and monitor attach.  The harness
  batches lines emitted within 200ms into one notification, so the
  catch-up grep arrives as a single event.
- **Poll Slurm state for completion, not the log.**  A pytest
  process can crash without writing a final line; `sacct` is
  authoritative.
- **Tight exit signaling.**  On completion, emit one clear marker
  line (`=== JOB X EXITED STATE=Y ===`), flush the log with a
  short `sleep`, tail the last few lines for immediate context,
  then `exit 0`.  No open-ended tails.

**What never belongs in the filter:** `PASSED`, `SKIPPED`,
progress percentages, `make[1]: Entering directory`, DVC pull
progress, raw parquet reads, INFO-level logs.  Anything that fires
more than once every few minutes under normal operation.

**Combining with cost tracking.**  At the end of a monitored
session, re-run `check_usage.sh -a <account>` to get the session's
SU delta.  Record both the job exit state and the SU cost in the
handoff note.

## Recording the Session

For long or complex sessions, keep a running handoff note (an org or
markdown file in `slurm_logs/` or equivalent).  Record:

- Date and brief session summary
- **Priority-account balance at session start and session end**
  (see [Cost Awareness](#cost-awareness)); the delta is the
  session's bill and tells the next reader what the session cost
- What was committed (hash + one-line description)
- What agents were dispatched and what they did (include Slurm
  job IDs and node names)
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

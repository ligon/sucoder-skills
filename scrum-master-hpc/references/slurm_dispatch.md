# Slurm Dispatch Reference

Guidance for submitting compute jobs to sibling nodes from an HPC login
or interactive session.  Written for Savio (UC Berkeley) but the
patterns generalize.

## Inspecting the Cluster

Before dispatching, survey what's available:

```bash
# What partitions can I submit to?
sacctmgr show assoc where user=$USER format=Account,Partition%30 --noheader

# What's the state of a specific partition?
sinfo -p savio4_htc --format="%N %C %m %f %T"

# What's my current utilization?
squeue -u $USER

# How much of the priority allocation is left?
check_usage.sh -a fc_jevons          # account balance
check_usage.sh -u $USER               # your personal usage
```

`check_usage.sh` lives at `/global/home/groups/allhands/bin/` on
Savio (on `$PATH` by default).  Example output:

```
$ check_usage.sh -a fc_jevons
Usage for ACCOUNT fc_jevons [2025-06-01, 2026-04-10]:
  2131 jobs, 26913.38 CPUHrs, 33270.11 SUs used from an allocation of 1500000 SUs.
```

The numbers that matter are **SUs used / SUs allocated**.  CPU-hours
and SUs diverge because partition multipliers vary by hardware.
Think in SUs when estimating cost.

For a per-user period breakdown:

```bash
sreport -t hours cluster accountutilizationbyuser \
    start=$(date -d '1 month ago' +%Y-%m-%d) end=now account=fc_jevons
```

See the [Cost Awareness](../SKILL.md#cost-awareness) section of
the main skill for the protocol around when and why to check.

Key fields in `sinfo` output:

- `%C` — CPUs `Allocated/Idle/Other/Total`; more idle = more headroom
- `%m` — memory per node (MB)
- `%f` — features (SSD, InfiniBand, GPU type)
- `%T` — state (idle, mixed, allocated, drained)

## Partition Selection

General guidance (tune to the cluster you're on):

| Need | Partition profile | Example (Savio) |
|---|---|---|
| Light tasks, parallel sweeps | HTC (high-throughput) with many cores/node | `savio4_htc`, 56 cores, 256–512 GB |
| Memory-hungry single tasks | bigmem with 256+ GB | `savio3_bigmem`, 384 GB |
| Long-running / preemption-sensitive | A partition your group owns | `fc_jevons`-allocated |
| Opportunistic / free | Low-priority on a co-investigator account | `co_carleton` / `savio_lowprio` |
| GPU work | GPU partition | `savio3_gpu`, `savio4_gpu` |

## Account choice: default to free

**Default to the free, low-priority account.**  On Savio this is
`co_carleton` (or the equivalent co-investigator account the group has
access to).  A fair-share / condo partition like `fc_jevons` is a
billed resource — every CPU-hour you spend on it draws down shared
compute budget the PI may be saving for end-of-term crunch or student
dissertation work.

Reserve the priority account for:

- Urgent work where preemption risk is unacceptable (paper deadline,
  live debugging during an interactive session)
- Jobs long enough that restart-on-preemption is expensive
- Work that genuinely cannot tolerate the low-prio queue wait

Everything else — test runs, data rebuilds, regression checks,
scatter-gather country sweeps, one-off scripts — should go on the
free low-prio account.  If a low-prio job gets preempted, resubmit
it; the cost of occasional restart is lower than the cost of
draining the shared budget.

**Ask before dispatching on a billed account.**  If you're a
scrum-master agent and you're about to submit to `fc_jevons` (or
equivalent), pause and surface the decision to the human first
unless they've already told you priority is warranted.

**Preemption**: Low-priority jobs can be evicted when a higher-priority
job claims the node.  For jobs under 1 hour, the risk is usually
acceptable.  For multi-hour jobs, either use a priority partition,
checkpoint regularly, or make the job idempotent so a re-run picks
up where it left off.

## Job Submission Template

Minimal single-task job (free low-prio account, modest ask,
saturate whatever the scheduler gives you):

```bash
sbatch \
  --account=co_carleton \
  --partition=savio4_htc \
  --qos=savio_lowprio \
  --cpus-per-task=8 \
  --mem=32G \
  --time=01:00:00 \
  --job-name=my_task \
  --output=slurm_logs/%x_%j.out \
  --error=slurm_logs/%x_%j.err \
  --wrap='cd /path/to/project && .venv/bin/python -m pytest tests/ -n "${SLURM_CPUS_ON_NODE:-$SLURM_CPUS_PER_TASK}"'
```

Two design choices worth explaining:

- **Modest request**: `--cpus-per-task=8` and `--mem=32G` are
  schedulable on essentially any HPC node (old and new hardware
  alike).  A request that only fits on the largest nodes locks you
  out of smaller partitions and makes preemption-on-resubmit far
  slower.  Ask for what the job actually needs plus a small
  cushion, not the full size of the biggest node you've seen.
- **Runtime saturation via `$SLURM_CPUS_ON_NODE`**: pytest reads
  `$SLURM_CPUS_ON_NODE`, which reflects **what Slurm actually
  gave you** — which may be more than `--cpus-per-task` if the
  partition is whole-node.  So you ask politely for 8 cores and
  use however many you end up with.  Fall back to
  `$SLURM_CPUS_PER_TASK` when `$SLURM_CPUS_ON_NODE` isn't set
  (some Slurm versions).

On genuinely shared partitions, you get exactly `--cpus-per-task`
and the two variables match.  On whole-node partitions,
`$SLURM_CPUS_ON_NODE` is larger and you saturate the bonus cores
instead of wasting them.

Common flags:

- `--account` — billing account (e.g., `fc_jevons` for priority,
  `co_carleton` for low-priority)
- `--partition` — which queue to submit to
- `--qos` — quality of service (often matches partition, but
  `savio_lowprio` for preemptible work)
- `--cpus-per-task` — how many cores the job needs
- `--mem` — memory (if omitted, defaults vary; be explicit)
- `--time` — wall-clock limit (`HH:MM:SS` or `D-HH:MM:SS`)
- `--job-name` — shows up in `squeue`
- `--output` / `--error` — stdout/stderr paths; use `%x` for job name
  and `%j` for job id
- `--wrap` — inline command; for more than one line, write a script

## Whole-Node Allocation: Saturate What You Get

On some clusters and partitions, **you are allocated the entire
physical node regardless of `--cpus-per-task`**.  Asking for 4 cores
on a 56-core node still blocks all 56; the other 52 sit idle for the
duration of the job.  This is true on Savio's condo / priority
partitions in particular, but can apply to HTC partitions depending
on site configuration, memory request, and QoS.

The temptation is to "just ask for all 56 cores up front" — but
that's the wrong fix.  A 56-core request only fits on the largest
nodes and locks you out of smaller hardware and most lower-priority
partitions, which is especially bad when you're preemptible.  The
right pattern is **ask modestly, saturate what Slurm actually gives
you**:

1. Request a schedulable amount (e.g. `--cpus-per-task=8`,
   `--mem=32G`) — enough for the work, schedulable on most nodes.
2. Inside the job, **saturate whatever you were handed** using
   `$SLURM_CPUS_ON_NODE` (the variable set by Slurm to reflect the
   cores the job was given on its node, which may exceed
   `--cpus-per-task` on a whole-node partition).

```bash
# Use the bonus cores if we got them; fall back to the request otherwise
NPROC="${SLURM_CPUS_ON_NODE:-$SLURM_CPUS_PER_TASK}"
.venv/bin/python -m pytest tests/ -n "$NPROC"
make -j"$NPROC"
xargs -P "$NPROC" ...
```

That way, a modest request gets you scheduled on any partition, and
a bonus whole-node allocation still gets saturated at runtime.  The
worst case (shared partition, exactly `--cpus-per-task` cores) still
uses what you asked for, with no waste.

Before deciding how modest to be, confirm whether your target
partition shares nodes or allocates them whole:

```bash
scontrol show partition savio4_htc | grep -iE 'shared|exclusive|oversubscribe'
sinfo -p savio4_htc --format="%N %C %m %T"
# If %C shows e.g. 132/204/0/336 with STATE=mixed, the partition is
# shared across users.  If jobs always show whole-node allocations,
# it isn't.
```

When you know the partition is whole-node:

- **Keep the request modest** for schedulability and preemption
  recovery, but **saturate at runtime** via `$SLURM_CPUS_ON_NODE`
  (see above).  Never hard-code a core count.
- **Use parallelism tools** that respect a passed-in N: `pytest -n
  $N`, `make -jN`, `parallel -j $N`, `joblib.Parallel(n_jobs=N)`,
  `xargs -P $N`.
- **Check memory**: don't let a single-threaded process balloon to
  the whole node's RAM while other cores sit idle.  Parallelism
  usually amortizes memory across workers, but peak memory per
  worker still matters.
- **Prefer shorter jobs**: a saturated 20-minute job is a much
  better queue citizen than a single-threaded 6-hour job on the
  same allocation, and far friendlier to preemption.

When you know the partition is shared (HTC configured for sharing):
request exactly what you need.  Over-requesting holds cores other
users could be running.  In this case `$SLURM_CPUS_ON_NODE` will
equal `--cpus-per-task` and the runtime saturation logic is still
correct — there's no downside to writing code that reads the
variable.

### Scale out, not up

If the work genuinely needs more cores than a modest single-node
ask gives, do not respond by hunting for one massive node.  Scale
**horizontally** instead:

- **Embarrassingly parallel work** (one task per country, one per
  file, one per seed): use an **array job** (see "Array Jobs"
  below).  Each element of the array runs on its own small
  allocation, and a preempted element costs only its own work, not
  the whole run.
- **Tightly coupled work** (MPI, Dask, distributed training):
  request **`--nodes=N` `--ntasks-per-node=K`** and let Slurm
  place the job across N nodes.  You get N × K workers without
  needing any single node to be huge.
- **Coordinator + workers**: run the coordinator on one small
  Slurm job and have it `sbatch` worker jobs for the parallel
  tasks.  The coordinator stays lightweight; the workers are
  replaceable.

Horizontal scale is friendlier to the scheduler (more partitions
fit a 4-core × 16-node job than a 64-core × 1-node job),
friendlier to preemption (losing one element of an array is
cheap), and friendlier to cost accounting (you only pay for what
you use).

### pytest on Slurm

Install `pytest-xdist` as a test-group dependency (`pip install
pytest-xdist` or add to `pyproject.toml` under the test group),
then let the job decide how many workers at runtime:

```bash
NPROC="${SLURM_CPUS_ON_NODE:-${SLURM_CPUS_PER_TASK:-1}}"
.venv/bin/python -m pytest tests/ -n "$NPROC"
```

`-n $NPROC` uses exactly the cores Slurm gave you — whether that's
the modest `--cpus-per-task` on a shared partition or the full
node on a whole-node partition.  `-n auto` is a reasonable fallback
but it guesses from `os.cpu_count()`, which can under-count in
containerized or cgroup-limited environments; `$SLURM_CPUS_ON_NODE`
is authoritative.

For I/O-bound test suites (e.g. data-pipeline integration tests
that read many files), parallelism hides per-test latency even when
CPU isn't saturated; a 10x speedup from 8 workers on a
file-reading workload is common.

Gotcha: xdist runs tests in separate worker processes, so any test
that writes to a shared on-disk cache or mutates a shared fixture
must be made concurrency-safe.  Most unit tests are fine; data-build
tests that share a parquet cache may need `--dist=loadfile` (group
tests by file into one worker) or explicit locking.

## Array Jobs (Parallel Sweeps)

For N independent tasks (e.g., one per country), prefer an array job
over submitting N separate `sbatch` commands:

```bash
#!/bin/bash
#SBATCH --account=co_carleton
#SBATCH --partition=savio4_htc
#SBATCH --qos=savio_lowprio
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --job-name=build_countries
#SBATCH --output=slurm_logs/%x_%A_%a.out
#SBATCH --array=0-29

COUNTRIES=(Uganda Malawi Tanzania Nigeria Niger Mali Ethiopia ...)
COUNTRY=${COUNTRIES[$SLURM_ARRAY_TASK_ID]}

cd /path/to/project
.venv/bin/python build_country.py "$COUNTRY"
```

Benefits: single submission, shared log directory, Slurm schedules
them efficiently, `scancel $JOB_ID` cancels the whole array.

## Environment Setup

Each job runs in a fresh shell, so set up the environment explicitly:

```bash
# Load modules if using Lmod
module load python/3.11

# Or use a project venv
source /path/to/project/.venv/bin/activate

# Set project-specific env vars
export PYTHONPATH=/path/to/project
export LSMS_SKIP_AUTH=1  # or whatever the project needs

# Move to the right working directory
cd /path/to/project
```

## Local Storage on Compute Nodes

Most HPC nodes have fast local storage (e.g., `/local/` or `/tmp/`)
that is much faster than the shared filesystem but **not visible from
other nodes**.

- **Use for**: temporary build artifacts, fast scratch I/O, copies of
  the venv for fast imports
- **Don't use for**: anything you need to retrieve after the job ends
  (unless you copy it back to shared storage before exit)

Pattern for a fast build:

```bash
# Copy venv to local disk for fast imports
cp -r /shared/project/.venv /local/venv
/local/venv/bin/python -c "import project; project.build()"

# Write outputs to shared storage
/local/venv/bin/python -c "project.write_output('/shared/project/out/')"
```

## Monitoring Running Jobs

```bash
# Live queue
squeue -u $USER

# Full info on a specific job
scontrol show job $JOBID

# Resource usage of running or completed jobs
sacct -j $JOBID --format=JobID,JobName,State,ExitCode,Elapsed,MaxRSS,CPUTime

# Tail a log
tail -f slurm_logs/my_task_$JOBID.out

# Cancel a job
scancel $JOBID
```

## DVC Lock Contention in Parallel Jobs

If multiple parallel jobs share a DVC repository root (e.g., all
running `dvc pull` against the same cache), they can leave stale
locks and deadlock.  Mitigations:

- Use `LSMS_BUILD_BACKEND=make` (or project equivalent) to bypass DVC
- Stagger job starts with `--begin=now+N` or a short `sleep $((RANDOM % 30))`
- If a stale lock persists, check `ps aux | grep dvc` for a running
  process; if none, delete the lock file manually

## Dispatching Agents vs. Slurm Jobs

These are complementary, not interchangeable:

| Use agents when... | Use Slurm when... |
|---|---|
| You need a language-model decision on the work | The work is a pure compute pipeline |
| You want a report back with interpretation | You want raw output artifacts |
| The task is small (seconds to a few minutes) | The task is long (minutes to hours) |
| The task benefits from context / judgment | The task is a deterministic script |

You can combine them: dispatch a coordinator agent that `sbatch`es
Slurm jobs and monitors them via the `squeue` CLI.  That agent stays
lightweight while the heavy compute runs on another node.

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

Minimal single-task job (free low-prio account, saturated node):

```bash
sbatch \
  --account=co_carleton \
  --partition=savio4_htc \
  --qos=savio_lowprio \
  --cpus-per-task=56 \
  --mem=0 \
  --time=01:00:00 \
  --job-name=my_task \
  --output=slurm_logs/%x_%j.out \
  --error=slurm_logs/%x_%j.err \
  --wrap="cd /path/to/project && .venv/bin/python -m pytest tests/ -n auto"
```

`--cpus-per-task=56` + `--mem=0` asks for all cores and all memory
on the node, which is appropriate when the partition allocates whole
nodes anyway (see "Whole-Node Allocation" below).  On a genuinely
shared partition, request exactly what the job needs.

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

## Whole-Node Allocation: Saturate What You Request

On some clusters and partitions, **you are allocated the entire
physical node regardless of `--cpus-per-task`**.  Asking for 4 cores
on a 56-core node still blocks all 56; the other 52 sit idle for the
duration of the job.  This is true on Savio's condo / priority
partitions in particular, but can apply to HTC partitions depending
on site configuration, memory request, and QoS.

**Implication**: if you're going to grab a whole node anyway, the
only responsible thing is to **saturate it**.  A 56-core node running
a single-threaded pytest is worse than wasteful — it's antisocial to
every other user waiting in the queue for those cores.

Before dispatch, confirm whether your target partition shares nodes
or allocates them whole:

```bash
scontrol show partition savio4_htc | grep -iE 'shared|exclusive|oversubscribe'
sinfo -p savio4_htc --format="%N %C %m %T"
# If %C shows e.g. 132/204/0/336 with STATE=mixed, the partition is
# shared across users.  If jobs always show whole-node allocations,
# it isn't.
```

When you are on a whole-node partition:

- **Request `--cpus-per-task` = all cores on the node**, not a polite
  fraction.  You have them anyway.
- **Use parallelism tools** to saturate: `pytest -n auto`, `make -jN`,
  `parallel`, `joblib.Parallel`, `xargs -P`, etc.
- **Check memory**: don't let a single-threaded process balloon to
  the whole node's RAM while other cores sit idle.  Parallelism
  usually amortizes memory across workers.
- **Prefer shorter jobs**: a saturated 20-minute job is a much better
  queue citizen than a single-threaded 6-hour job on the same
  allocation.

When you are on a shared partition (HTC configured for sharing):
request exactly what you need.  Over-requesting holds cores other
users could be running.

### pytest on a whole-node allocation

Install `pytest-xdist` as a test-group dependency (`pip install
pytest-xdist` or add to `pyproject.toml` under the test group).  Then
invoke pytest with:

```bash
.venv/bin/python -m pytest tests/ -n auto
# or, to be explicit:
.venv/bin/python -m pytest tests/ -n "$SLURM_CPUS_ON_NODE"
```

`-n auto` lets xdist pick up all available cores.  For I/O-bound
test suites (e.g. data-pipeline integration tests that read many
files), parallelism hides per-test latency even though CPU isn't
saturated; a 10x speedup from 8 workers on a file-reading workload
is common.

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

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
```

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

**Preemption**: Low-priority jobs can be evicted when a higher-priority
job claims the node.  For jobs under 1 hour, the risk is usually
acceptable.  For multi-hour jobs, use a priority partition or
checkpoint regularly.

## Job Submission Template

Minimal single-task job:

```bash
sbatch \
  --account=co_carleton \
  --partition=savio4_htc \
  --qos=savio_lowprio \
  --cpus-per-task=4 \
  --mem=16G \
  --time=01:00:00 \
  --job-name=my_task \
  --output=slurm_logs/%x_%j.out \
  --error=slurm_logs/%x_%j.err \
  --wrap="cd /path/to/project && .venv/bin/python my_script.py"
```

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

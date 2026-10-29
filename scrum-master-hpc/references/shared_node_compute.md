# Heavy Compute on a Shared Node

Two disciplines for heavy work on the same many-core node as the
interactive session: pinning JAX/XLA suites so they do not segfault
each other, and niceing background jobs so the session stays
responsive.

## Running JAX/XLA suites on a shared many-core node

JAX/XLA is a special case of oversubscription that bites *harder* than the
`pytest -n auto` rule in SKILL.md (Dispatch Modes, mode 4) — and the fix is different.

**The hazard.**  XLA sizes its JIT thread pool to the number of *visible*
CPUs and `mmap`s executable pages per worker.  So two or more *uncapped*
JAX processes on, say, a 64-core node spin up `2 × 64` threads plus double
the executable-page mmaps and **segfault** — a hard kill mid-run, often
with no pytest summary line, not the graceful slowdown ordinary
oversubscription gives.  This is the most likely cause of a mid-session
"the suite just died" on a fat node, and it strikes any multi-agent setup
where several agents each run a JAX `pytest`.

**The fix: pin to disjoint core sets with `taskset`, don't serialize.**
XLA sizes its pool to the *affinity-limited* CPU count
(`len(os.sched_getaffinity(0))`), so `taskset -c 0-31` makes a JAX process
behave as a 32-core process — fewer threads, fewer mmaps, confined cores.
Pin concurrent suites to disjoint halves and they coexist at full speed:

```bash
# two JIT-heavy suites, concurrently, on one 64-core node:
XLA_FLAGS=--xla_force_host_platform_device_count=1 taskset -c 0-31  pytest <A> &
XLA_FLAGS=--xla_force_host_platform_device_count=1 taskset -c 32-63 pytest <B> &
```

Validated: two JIT-heavy suites pinned to `0-31` / `32-63` both pass
concurrently with no segfault — and each is ~20× faster than the
ultra-safe `OMP_NUM_THREADS=1` single-thread fallback (which forces one
thread).  Even a *single* run benefits from `taskset -c 0-31`: a fast
32-core run that leaves the other half free.  **Multi-agent rule:** give
each agent a distinct core range, not an instruction to serialize.

(This is local-node discipline.  Under a cgroup-limited Slurm job the
affinity is already restricted — read `$SLURM_CPUS_ON_NODE` per
SKILL.md's mode 4 rules; you rarely need `taskset` there.)

**Pitfall — the self-matching wait loop.**  Do *not* gate a "wait for the
other suite to finish" loop on `pgrep -f "pytest"`: the loop's own command
line contains the string `pytest`, so `pgrep` matches *itself* and the loop
never exits.  This silently hangs an agent forever.  Match the concrete
process (`pgrep -f "bin/python -m pytest"`, excluding your own PID) — or,
better, just pin with `taskset` and skip the wait entirely.

## Keep the interactive session responsive: `nice` shared-node jobs

When the heavy background compute runs on the **same node** as your
interactive session (a parallel build sweep, a cross-country scan,
`pytest -n`, a `make -j`), it competes with the very session the user is
typing into.  A saturating `--jobs N` run at normal priority makes the
scrum master's own tool calls lag — defeating the "stay interactive"
principle in SKILL.md.  Cheap fix: **`nice` (and `ionice`) the job** so the
kernel preempts it in favour of interactive work.

```bash
# nice is inherited by children, so nicing the parent covers the whole
# worker pool; ionice -c 3 (idle) yields the disk too (DVC reads / parquet
# writes).  Both are unprivileged.
nice -n 19 ionice -c 3 .venv/bin/python scan.py --jobs 28 ...
```

- **Nice the launch, not after the fact.**  Re-nicing a running 30-worker
  pool means chasing every child PID.  Set it at `run_in_background` time.
- **Still leave headroom.**  `nice` makes the job *yield*, but a few free
  cores (`--jobs $((nproc-4))`) keep latency low even under contention.
- **Reaping orphans: do NOT `pkill -f "scan.py"`.**  Its own command line
  contains `scan.py`, so `pkill` SIGTERMs the shell running it (observed:
  the launching bash dies with exit 144) — the same self-match trap as the
  wait loop above.  Stop the *harness-tracked* background task instead
  (clean, reaps the worker pool); if you must `pgrep`/`kill` by hand, use
  the bracket trick (`pgrep -f '[s]can.py'`, which doesn't match its own
  argv) and exclude your own PID.
- **Or get off the node entirely.**  If the run is big enough that even a
  niced sweep churns the session, dispatch it to Slurm (separate node) per
  the [dispatch rules](../SKILL.md#4-slurm-job-separate-node) — niceness is a
  same-node palliative, Slurm is the real isolation.

# Headless Agent Workers with `sucoder dispatch`

How to hand an independent LLM task to a headless Codex or Claude worker
on another Slurm node, and get reviewable work back.  This is dispatch
mode 5 in SKILL.md: unlike a raw `sbatch` job, the worker is a model
that reads steering at checkpoints; unlike an in-process agent, it gets
its own allocation, node-local state and private result repository.

`sucoder dispatch` is new: no tagged SuCoder release contained it when
this was written.  Run `sucoder dispatch --help` (outside a source
checkout) before relying on it; the help states each subcommand's exit
codes, and the full reference is `docs/dispatch.org` in
https://github.com/ligon/sucoder.

## When to use it

- The task needs model judgment *and* more time, cores or isolation than
  an in-process agent should take from the coordinator's node.
- Several independent assignments should run concurrently on different
  nodes (an implementer and a reviewer, or a sweep).
- You want the work back as commits to review, not as edits in your tree.

For deterministic compute (pytest, make, a build) use mode 4 instead;
for a frozen verification run of one exact commit, see `dispatch
verify-stage` in the same help.

## The contract, in the order you meet it

1. **Run it on the cluster, as yourself.**  Dispatch uses the current
   Slurm cluster and account.  `-T`/`--target` and `--config` are
   refused, and `--root` (the private record directory, on shared
   storage) goes *before* the subcommand:
   `sucoder dispatch --root DIR status ID`.
2. **Source: a committed revision of a full repository on shared
   storage.**  `--ref` is resolved to one commit before submission.
   Uncommitted edits are not sent, and a `/local/job…` checkout or a
   partial clone is refused.  Commit first, then dispatch.
3. **The task file is the whole assignment.**  Its content is frozen at
   submission; write the concrete task, the checks to run and the
   report you want into it.  Later steering goes through the channel
   below, not by editing the file.
4. **Ask for resources explicitly.**  `--account`, `--partition`
   (and `--qos` where needed), `--cpus`, `--mem`, `--time`.  The
   free-account rule from mode 4 applies.  `--time` must be at least two
   minutes (a 120-second TERM window is reserved), and
   `--exclude <coordinator node>` keeps the worker off your own node.
   Use `--dry-run` first: it validates everything and prints the
   planned `sbatch` line without writing or submitting anything.
5. **Read submit's exit status.**  0 submitted; 1 `sbatch` could not
   run (no job exists); 2 refused.  **3 is `submission_unknown`: Slurm
   may already have the job.  Never resubmit blindly** — look for the
   job comment `sucoder-dispatch:<dispatch-id>` (for example
   `squeue --me -o '%i %k'`) and reconcile first.
6. **Address it by dispatch ID**, the 32-character ID that submit
   prints, not the Slurm job number.

## Steering and questions

Each dispatch directory already contains `MESSAGES_TO_AGENT.txt` and
`QUESTIONS_FROM_AGENT.txt`, created before the worker starts, and the
worker's prelude names their paths.  **Do not create your own channel
files for a dispatched worker** (Pattern 8 in dispatch_patterns.md is
for workers you launch yourself); append steering to the existing
`MESSAGES_TO_AGENT.txt` and poll `QUESTIONS_FROM_AGENT.txt`.

## Observing and finishing

- `status ID` — phase, heartbeat age, publication facts.  A fresh
  heartbeat proves the supervisor is alive, not that the task is
  progressing.
- `logs ID --stream stderr|stdout|scheduler|scheduler-stderr` — a
  bounded tail; works while the worker runs.
- `wait ID --timeout SECONDS` — succeeds only on an explicit successful
  result.  With `--require-task-complete` it also requires the worker
  to have reported its task `completed`, and exits 4 otherwise.  A
  worker's own exit code can collide with 2–4; the printed JSON is
  authoritative.
- `result ID` — the final record, separating native and supervisor
  exit, placement, Git/evidence publication, conversation preservation
  and the worker's task report (`completed`, `blocked`, `unfinished` or
  `scientific_disagreement`).  It exits 0 with `result_state: missing`
  while the worker is still running.

Infrastructure success is not acceptance.  The coordinator still
reviews the work.

## Getting the work back

The worker commits to branch `dispatch/<dispatch-id>` in a private
`results.git` inside the dispatch directory, never to the source
repository.  Periodic and final WIP snapshots publish there too
(`--snapshot-minutes`, default ten); SIGKILL loses anything after the
last published snapshot.  Fetch the branch, review it like any
delegated work (see Message Discipline in SKILL.md), and integrate it
yourself; nothing merges or retries automatically.

Proof files the worker should hand back (JUnit XML, logs) go in the
directory named by `SUCODER_DISPATCH_EVIDENCE_DIR`.  Pass
`--require-evidence junit.xml` (repeatable) to make a missing proof
file an infrastructure failure rather than a silent omission.

## Traps

- **Do not test nested real Codex workers under a managed Codex
  coordinator** whose placement monitor owns its descendants; submit
  them from an ordinary shell or allocation instead.
- **An installed `sucoder` can lag the source.**  If a subcommand or
  option in this file is missing, check `sucoder --version` and
  `sucoder dispatch --help` before concluding the feature is absent.
- **The source must be reachable from the receiving node.**  A path
  under the coordinator's `/local` or `/tmp` is refused for that reason;
  the same applies to `--executable` and `--agent-home`.

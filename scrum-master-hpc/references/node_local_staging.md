# Node-Local Staging

How to use a compute node's local SSD (`/local`) instead of the shared
filesystems, and — more often — how to decide you shouldn't bother.
Written for Savio (UC Berkeley); the reasoning generalizes to any cluster
with node-local scratch, but every number below was measured there.

## The three filesystems are each bad at something different

Measured on `n0030.savio4`, 2026-08-25.  Home is VAST NFS; scratch is
Lustre; `/local` is a node-local ext4 SSD.

| operation | NFS `$HOME` | Lustre scratch | `/local` |
|---|---|---|---|
| import a 12k-file Python venv (warm) | 1.7 s | **6.7 s** | 1.1 s |
| single binary startup | 0.07 s | 0.31 s | 0.05 s |
| Lean `import Init` (mmap'd oleans, warm) | — | **11 s** | 0.25 s |
| create+list+delete 2000 small files | **86 s** | 20 s | 0.10 s |
| `uv venv` + install one package | **47 s** | 2.6 s | 2.4 s |
| `flock` | **fails (ENOLCK)** | works | works |

Three consequences worth internalizing:

- **NFS home cannot lock.** `flock` returns `ENOLCK`.  Anything with a
  SQLite database or a lockfile — most modern agent harnesses, many
  tools' config writers — fails outright there, sometimes as a 30-second
  hang rather than an error.  Such state must live on Lustre or `/local`.
- **Lustre is the *worst* filesystem here for read-hot small files**, which
  is the opposite of the usual intuition.  It is good at writes and it is
  the only large persistent space, so things get put there — and then
  reads get 4-6x slower.  That gap is what staging buys back.
- **NFS home is catastrophic for metadata writes** — 86 s to create 2000
  files.  Never build, install, or unpack there.

## Decide before you stage

Staging is worth it when **all three** hold:

1. the tree is **read-hot** — re-read on every process launch, not once;
2. it has **many files** — thousands, so per-file latency dominates; and
3. it currently lives on **Lustre** (or another slow-for-reads share).

If it is already on NFS home and read-hot, staging gains little: an aider
venv measured 1.7 s → 1.1 s, only 1.5x, because ~1 s of that is CPU, not
I/O.  Not worth the moving parts.

Do **not** stage anything that must survive the job, take a lock, or be
written by others.  `/local/job$SLURM_JOB_ID` is reclaimed when the job
ends.  Everything staged must be reconstructible from its source, which
is also why no sync-back or copy-on-write layer is needed — if you find
yourself wanting one, you are staging the wrong thing.

The big wins are read-hot trees stuck on Lustre because they need locks
or space.  The canonical example is a Lean toolchain plus mathlib
`.olean` files: **0.25 s from `/local` versus 11 s from Lustre, steady
state.**  Lustre never converges here — repeated runs stay at ~11 s,
because the oleans are large and mmap'd and the client cache does not
rescue them.

## Prefer a single-file image over a tar-pipe

The reason is **not** your own wall-clock — it is the metadata server you
share with everyone else on the cluster.  A venv or toolchain is tens of
thousands of inodes; reading it file-by-file off Lustre is an MDS storm.
An image is **one inode**.

Ranked, fastest and most considerate first:

1. **squashfs image + FUSE mount.**  One shared-filesystem inode, no
   extraction at all.  `squashfuse` is not installed standalone on Savio,
   but apptainer bundles it at
   `/usr/libexec/apptainer/bin/squashfuse_ll`, and `/dev/fuse` is
   world-writable with unprivileged user namespaces enabled.
2. **squashfs or tar.zst image, extracted to `/local`.**  Still one inode
   read from the share; costs a local unpack, which is cheap (0.7 s for
   12k files).  Use when you need real files rather than a mount.
3. **tar-pipe from the source tree.**  Reads every file individually off
   the share.  Works, but it is the MDS-hostile path — a fallback, not a
   default.
4. **`cp -a` of the tree.**  Never.  Measured 343 s for the same 12,185
   files a tar.zst extract does in 1.5 s and an unsquashfs in 0.7 s.

Build the image once and rebuild it only when its source changes.
Checksum it (`SHA256SUMS`) and *verify before use* — a silently truncated
or stale image is far more expensive to diagnose than to prevent.

## Use the implementations that already exist

Four independent versions of this have been written in this workspace.
Read these before writing a fifth:

- **`LSMS_Library/bin/savio_venv.sh`** — the reference implementation of
  the image approach.  `.venv.lustre/` is the writable master,
  `.venv.sqfs` the read-only image (~255 MB, one inode instead of ~33k),
  and `.venv` a per-job symlink to a squashfuse mount at
  `/local/$SLURM_JOB_ID/venv`.  Subcommands `update` / `mount` /
  `umount`; falls back to `unsquashfs` extraction when FUSE is
  unavailable.  See `LSMS_Library/docs/savio_venv.md`.
- **`AggregationWithLimitedCommitment/tools/resolve-lean-env.sh`** — the
  most developed version.  Probes viability, prefers an already-staged
  copy, stages from a checksum-verified `tar.zst` and falls back to a
  tar-pipe, keys the store on toolchain + `sha8(lake-manifest.json)` so
  several projects share one copy, and selects via environment variables
  (`ELAN_HOME`, `LEAN_PATH`, `LEAN`) rather than symlinks.  Do not
  bypass it by setting `ELAN_HOME` yourself; it reads that variable as
  the location of the *source*, and repointing it corrupts the decision.
- **`AggregationWithLimitedCommitment/tools/stage4_{inner,outer}.sbatch`**
  — a 9-line `stage_tarball` helper (checksum-gated `zstd | tar -x`),
  currently duplicated byte-for-byte between the two files.

Shared artifacts live in
`/global/scratch/fsa/fc_jevons/ligon/sue-scratch/stage-cache/` with
`SHA256SUMS` and a `SOURCES` log.

## Traps

**Probe the real access pattern, not a proxy.**  `resolve-lean-env.sh`
originally gated on `lean --version` — toolchain *exec* only.  That
passed off Lustre, so it selected Lustre, and the resulting
`import Mathlib` check ran over 22 minutes without finishing, twice, with
the process unkillable in `D` state.  The probe now elaborates a real
`import Mathlib` under a bounded timeout.  Whatever you stage, time the
operation you actually care about.

**A timeout is a stall; a fast failure is not.**  An `import` that fails
in milliseconds means a missing or broken build, not a slow filesystem.
Treating it as a stall triggers a pointless multi-GB stage.

**Staged venvs silently escape back to the source.**  A console script's
shebang is an absolute path (`#!/…/venvs/aider/bin/python`), so running
the *staged* copy re-enters the *original* tree — and it benchmarks as
working while importing everything over the slow filesystem.  Either
invoke via `<staged>/bin/python -m <module>`, or build the venv with
`uv venv --relocatable`, which emits `#!/bin/sh` wrappers that resolve
`./python` relatively.  (A `#!/bin/sh` or `/usr/bin/...` shebang is fine
— system interpreters exist identically on every node.  The trap is a
shebang naming *another tree*.)

**`/local` is per-job and reclaimed.**  Do not build cross-job caching on
it.  `/local` itself is root-owned and not user-writable at top level on
savio4, so a persistent per-user directory there cannot be created;
`/local/job$SLURM_JOB_ID` is the only writable root, and it disappears
with the job.  On a login node there is no `$SLURM_JOB_ID` at all — any
staging helper must degrade to using the canonical copy rather than
failing.

**Leave multi-GB trees identifiable.**  `/local` on a shared node
accumulates abandoned job directories — on one savio4 node, other users'
dirs dating to 2022.  Write a `README.txt` next to anything large saying
who owns it, what it is, and that deleting it is safe.

## Related

- `slurm_dispatch.md` — submitting work to sibling nodes.
- The `carleton-htc` / `savio-node` target prompts cover allocation and
  turnover discipline; this file covers only filesystem strategy.

# Cost Accounting on Savio

The tooling behind SKILL.md's Cost Awareness protocol: where the usage
numbers come from, the `check_usage.sh` compute-node breakage and its
patch, Slurm-native fallbacks, and the start-of-session sanity check.
Savio-specific; generalize the commands to your cluster.

# Knowing the numbers

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

**`check_usage.sh` is broken on Savio compute nodes.**  The script
(Python 2.7, last touched Sep 2025) chooses its config file by
checking `'brc' in socket.gethostname()`.  Compute node hostnames
are `n####.savio2` — no "brc" substring — so the script falls into
MyLRC mode and tries to read `check_usage_mylrc.conf`, which does
not exist in the `allhands/bin` directory.  You get
`config file /global/home/groups/allhands/bin/check_usage_mylrc.conf missing...`
and no data.  The login node hostname *does* contain "brc", so the
script works there.

**Recommended fix (one-time): drop a patched copy into
`~/.local/bin`** (which is typically ahead of
`/global/home/groups/allhands/bin` in `$PATH`, so your copy
shadows the broken one):

```bash
mkdir -p ~/.local/bin
cp /global/home/groups/allhands/bin/check_usage.sh       ~/.local/bin/
cp /global/home/groups/allhands/bin/check_usage_mybrc.conf ~/.local/bin/
chmod +x ~/.local/bin/check_usage.sh

# Replace the one-line MODE detection with env-var-first,
# savio-aware logic.  The CONFIG_FILE lookup keys on
# os.path.dirname(__file__), so the config file must live next to
# the script — hence copying it alongside.
python3 - <<'PY'
import pathlib, re
p = pathlib.Path.home() / ".local/bin/check_usage.sh"
src = p.read_text()
old = "MODE = MODE_MYBRC if 'brc' in socket.gethostname() else MODE_MYLRC"
new = '''# PATCHED: respect CHECK_USAGE_MODE env var, then detect "savio"
# in the hostname as a fallback so Savio compute nodes (whose
# hostnames do not contain "brc") are classified as mybrc.
_cu_hostname = socket.gethostname()
if os.environ.get('CHECK_USAGE_MODE') in (MODE_MYBRC, MODE_MYLRC):
    MODE = os.environ['CHECK_USAGE_MODE']
elif 'brc' in _cu_hostname or 'savio' in _cu_hostname:
    MODE = MODE_MYBRC
else:
    MODE = MODE_MYLRC'''
assert old in src, "upstream script has changed; re-audit"
p.write_text(src.replace(old, new))
PY

hash -r
check_usage.sh -a <priority_account>  # should now return data
```

The patch is two surgical changes: (1) the MODE-detection block
in `check_usage.sh`, (2) a copied `check_usage_mybrc.conf` next to
it so the config-file lookup (`os.path.dirname(__file__)`)
resolves.  The upstream Python-2.7 shebang and all other logic are
left intact.  The `assert old in src` line is a guard: if LBL
updates the upstream script, the patch will refuse to apply rather
than corrupt a newer version.

If you cannot or will not patch the script (e.g., brief session,
read-only home), the Slurm-native fallbacks below cover the
operational need:

```bash
# Cumulative usage this allocation period for the priority account,
# broken down by user.  Gives CPU-hours — convert to SUs by
# multiplying by the partition multiplier if you need the bill.
sreport -t hours cluster accountutilizationbyuser \
    start=$(date -d '1 month ago' +%Y-%m-%d) end=now \
    account=<priority_account>

# Fair-share weights and raw usage — useful for diagnosing queue
# position and checking your personal recent load.
sshare -A <priority_account> --all

# Your currently-running and queued jobs against the account
squeue -u $USER -A <priority_account>
```

What `check_usage.sh` adds on top of these is a single "SUs remaining
of allocation" number, which `sreport` alone does not give you —
you'd need to subtract cumulative usage from the allocation ceiling,
and the ceiling is not queryable via Slurm.  In practice, if the
login-node `check_usage.sh` run at session start gave you a ceiling
number, the session-end delta from `sreport` is the right thing to
diff against it.  If you never had a ceiling number (compute-node-
only session), record the session's `sreport` delta as raw CPU-hours
and let the human map it to their allocation themselves.

# Sanity-check the tool before relying on it

At the start of each session, verify that your usage tool is
actually returning data before you record a baseline:

```bash
check_usage.sh -a <priority_account> 2>&1 | head -5
```

If the output is a config-missing error, a token error, a network
timeout, or empty, **do not record an incorrect "session start
balance"** in the handoff — that will poison the end-of-session
delta.  Either move to a node where the tool works, switch to the
`sreport`-based fallback and mark the handoff with "CPU-hours
only, no SU ceiling", or ask the human for the current balance.

**Empirical update (2026-04-28).**  `check_usage.sh -a <account>`
returned valid usage data on at least one Savio compute node
(`n0291.savio2`) without needing the patch documented above.  The
patch may still be necessary on other nodes — the cluster
admin's deployment may not be uniform — so the recommended order
is: try the unpatched script first, fall through to the patch
recipe (or the `sreport`-based fallback) only if it fails.  Don't
preemptively apply the patch.

# Compatibility scenarios

Checked against the SuCoder P1/P2 source changes based on commit
`164913d2e67c782d4a25e70b3710888a03edbb2e` (2026-10-22). These are deterministic
recipe walkthroughs and service tests, not live model or cluster trials.

| Situation | Supported action | Required interpretation |
|---|---|---|
| Older CLI lacks context/JSON | Use local git facts; retain unknown remote facts | Do not parse human tables into the version 1.0 contract |
| Current CLI, no MCP | Use `context --json` and `sessions --json` | MCP absence does not block the task |
| Future optional MCP adapter present | Check actual advertised tools/schema and launch binding | No server is supplied or integration verified by P1/P2 |
| Local git checkout, no mirror mapping | Read git root/HEAD; keep mirror unknown | Complete git observation does not imply configured durability |
| Configured node-local clone | Require unique configured work-path and local origin mapping | Durable path is reported placement, not publication proof |
| Workspace symlink retargeted | Reject changed binding; inspect intended cwd again | Do not reuse the earlier identity |
| One unreachable target | Use other sources, retain failed source as unknown | No false absent/stale record verdict |
| Proven empty source | Check complete coverage and count zero | Empty only within that source and observation interval |
| Relay absent or older version | Report `RELAY_UNSUPPORTED`/unavailable | No terminal-table fallback, sudo changes, or installation repair |
| Equal job IDs across sources/accounts | Keep source IDs attached through every comparison | No cross-source record match |
| Mixed replacement holders | Preserve per-job matched/absent evidence and aggregate unknown | Never recommend clearing from the aggregate |
| Truncated result | Narrow target and rerun | Omitted attribution is unknown, not an empty target list |
| Peer visible | Inspect identity and user authorization before message/peek | Discovery alone authorizes neither sending nor reading pane content |

Reproduce code cases with `pytest -q tests/test_observations.py` from the SuCoder
checkout. Run `make check` from sucoder-skills for catalog and formatting checks.
The skill smoke test uses local catalog construction; no `collaborate` launch,
allocation, or model call is needed to validate discoverability.

---
name: sucoder-session
description: >-
  Use this skill to establish a SuCoder agent's workspace identity, distinguish
  a durable mirror from a node-local working clone, and interpret bounded
  context observations before making claims about storage or allocation state.
license: Apache-2.0
---

# SuCoder Session Context

## Trigger

Load when starting work in a SuCoder session, checking which clone holds the
work, or preparing a handoff that needs accurate workspace and storage facts.
Use [sucoder-peers](../sucoder-peers/SKILL.md) for peer discovery.

## Actions

1. Check the installed interface with `sucoder --version` and
   `sucoder --help`. If `context` exists, check `sucoder context --help`.
   Source-tree features need not be installed on this host.
2. From the actual working directory, run the supported command:

   ```sh
   sucoder context --json --timeout 5
   ```

   Preserve stdout even on a nonzero exit. Parse it as one JSON object; accept
   exactly `schema_version: "1.0"`. Exit 0 means complete, 3 means partial or
   unavailable, 2 means invalid arguments/configuration, and 1 means an internal
   or response failure. Missing output, malformed JSON, or another version is
   unavailable evidence, never an empty workspace.
3. Read `data.binding`, the fact states, and `coverage` before drawing a
   conclusion. `observed` describes local evidence; `reported` describes a
   configuration or environment claim. Unknown or ambiguous facts have null
   values. A null observed branch can mean detached HEAD; a null observed HEAD
   can mean an unborn repository.
4. Compare `requested_workspace` and `git_root` to the intended checkout.
   If binding changed, stop using that observer and inspect again from the
   intended directory. Do not repair paths or select a different clone merely
   to make the result complete.
5. Treat `durable_mirror` as configured placement, not proof of publication.
   Check the repository's normal status and publication workflow before a
   handoff. A post-commit hook, a commit in a temporary clone, or an environment
   variable does not prove that work reached durable storage.

`SLURM_JOB_ID` and `SUCODER_LOCAL_ROOT` are reported environment facts; neither
proves a live allocation or authorizes its release. Confinement stays unknown
unless the applicable configuration is identifiable. A local-tier mapping
requires a unique configured layout and matching configured local-path origin;
an origin URL alone is insufficient.

## Compatibility and fallback

If `context --json` is absent, inspect `pwd -P`, `git rev-parse --show-toplevel`,
`git status --short --branch`, and project guidance. Label those as local git
facts. Report unknown durability, target, and confinement where evidence is
missing. Do not install, provision, change accounts, or repair SSH to inspect.

No SuCoder MCP server ships with this skill. Use the CLI without MCP. If a
separately installed adapter is available in a future environment, check its
advertised tools and schema before using it; do not invent a `session_context`
tool or install the design document's fictitious example executable.

## Pitfalls

- Do not interpret context as a global inventory of sessions or storage.
- Do not infer "safe to release/delete" from any observation field.
- Keep raw origins, credentials, pane content and full configuration out of
  feedback reports. Use [skill-feedback](../skill-feedback/SKILL.md) for a
  concrete skill defect within the user's reporting authorization.
- Do not silently accept a new schema version, even a minor version.

## References

- [Compatibility scenarios](references/scenarios.md): acceptance cases and
  implementation baseline, including older CLIs and unavailable discovery.
- SuCoder's `docs/agent-interface-contract.org` and
  `docs/agent-interface/response.schema.json`: the version 1.0 wire contract.

## Changelog

- **2026-10-22**: Added for the reviewed P1/P2 observation interface. Check local
  help for installation support; implementation in a source tree is not a
  deployment claim.

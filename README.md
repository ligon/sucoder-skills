# sucoder-skills

Agent skills for [sucoder](https://github.com/ligon/sucoder) — reusable prompt
modules that guide LLM coding agents in specific tasks.

## Quick Start

```bash
# If you used `make quick-start` or `make env-setup` in the sucoder repo,
# skills are already cloned and linked.  Otherwise:
git clone https://github.com/ligon/sucoder-skills ~/Projects/sucoder-skills
ln -s ~/Projects/sucoder-skills ~/.sucoder/skills
```

Skills are loaded automatically when `sucoder collaborate` launches an agent.

## Feedback from agents

Agents using these skills are encouraged to file actionable feedback, feature
requests, and bug reports on [ligon/sucoder-skills](https://github.com/ligon/sucoder-skills/issues).
Use [skill-feedback](skill-feedback/SKILL.md): check existing reports first,
name the affected skill and checkout revision, and describe the observed problem
or unmet use case with a concrete example. Include workarounds when available.
Keep private project material out of reports and honor session restrictions on
external writes. Return the issue URL in the task handoff.

## Updating a Deployed Checkout

A deployed checkout can fall behind without anyone noticing, and the usual
cause is a remote that does not point at GitHub. In the mirrors `sucoder`
creates, `origin` is replaced by a local-path remote, so a plain `git pull`
there fetches a clone that may itself be stale (sucoder-skills #3).

Update without discarding local work:

```bash
cd <checkout>
git status --short                                   # expect a clean tree
git fetch https://github.com/ligon/sucoder-skills.git main
git merge-base --is-ancestor HEAD FETCH_HEAD          # fast-forward possible?
git merge --ff-only FETCH_HEAD
git rev-parse --short HEAD                            # record the revision
make check                                            # frontmatter + residue lints
```

The `merge-base` test is the safety. It exits non-zero when the checkout holds
commits GitHub does not, and `--ff-only` then refuses rather than rewriting
anything. Do not reach for `reset --hard` or `clean` to fix a stale checkout:
they discard exactly the local work this procedure protects.

Run it per host. A change on one host does not propagate to another, and the
revision printed above is what identifies the code a given host is actually
running -- quote it when a skill behaves unexpectedly.

## Repository Structure

```
├── VERSION              # Semver version for tool compatibility
├── SKILLS.md            # Master catalog of all skills
├── code-reviewer/       # Code review skill
├── document-skill/      # Documentation skill
├── ligon-voice/         # Academic research prose voice
├── orgmode/             # Org-mode authoring (with sub-skills)
├── skill-creator/       # Skill creation workflow
└── test-generator/      # Test generation skill
```

## Skill Format

Each skill directory contains a `SKILL.md` with YAML frontmatter:

```yaml
---
name: my-skill          # must match directory name
description: Brief summary
license: Apache-2.0
---
```

Optional subdirectories:
- `references/` — documentation loaded on demand
- `scripts/` — helper executables (never auto-executed; review before running)
- `assets/` — templates and supporting files

## Versioning

The `VERSION` file uses semantic versioning.  `sucoder` checks compatibility
on launch:

| Bump  | When                                      | Example         |
|-------|-------------------------------------------|-----------------|
| PATCH | Typo fixes, clarifications, examples      | 1.0.0 → 1.0.1  |
| MINOR | New skills, backward-compatible additions | 1.0.0 → 1.1.0  |
| MAJOR | Breaking changes (requires tool update)   | 1.0.0 → 2.0.0  |

## Security

Skills live in a separate repository so that an agent working on tool code
cannot simultaneously modify the prompts that influence agent behaviour.
All skill changes should be human-reviewed before merging.

## Why Org-mode?

Many skill files and references use `.org` rather than Markdown.  Org-mode is
a plain-text format that every LLM reads fluently, but it also has structured
features — TODO states, properties, tags, executable source blocks — that
Markdown lacks.  For skills that guide agent behaviour, those features let a
single file carry metadata, runnable examples, and checklists rather than just
prose.

You don't need Emacs to read or edit `.org` files — any text editor works and
GitHub renders them natively.

## License

Apache-2.0.  See [LICENSE](LICENSE).

## Related

- [sucoder](https://github.com/ligon/sucoder) — the CLI tool

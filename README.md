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

## Repository Structure

```
├── VERSION              # Semver version for tool compatibility
├── SKILLS.md            # Master catalog of all skills
├── code-reviewer/       # Code review skill
├── document-skill/      # Documentation skill
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

## License

Apache-2.0.  See [LICENSE](LICENSE).

## Related

- [sucoder](https://github.com/ligon/sucoder) — the CLI tool

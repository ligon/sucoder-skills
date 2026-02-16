# Coder-Collab Skills

Agent skills for the `coder-collab` toolkit - specialized instruction sets that guide AI agents in performing specific tasks.

## Overview

This repository contains skills that are loaded into agent sessions by the `coder-collab` tool. Skills provide:
- Domain-specific knowledge (e.g., Org-mode authoring, code review)
- Specialized workflows and best practices
- Supporting resources (scripts, templates, references)

## Repository Structure

```
.
├── VERSION                    # Semver version for compatibility checking
├── SKILLS.md                  # Master catalog of all skills
├── code-reviewer/            # Code review skill
│   └── SKILL.md
├── document-skill/           # Documentation skill
│   └── SKILL.md
├── orgmode/                  # Org-mode authoring
│   ├── SKILL.md
│   ├── references/          # Supporting documentation
│   ├── scripts/             # Helper scripts (not auto-executed)
│   └── assets/              # Templates and examples
├── skill-creator/           # Skill creation workflow
├── test-generator/          # Test generation skill
└── tests/                   # Skill validation tests
```

## Skill Format

Each skill follows the [Anthropic Agent Skills Spec](https://docs.anthropic.com/agent-skills):

- **SKILL.md**: Entrypoint with YAML frontmatter containing:
  - `name`: Must match directory name
  - `description`: Brief summary
  - `license`: License type (e.g., Apache-2.0)
  - Optional: `allowed-tools`, `metadata`

- **Subdirectories** (optional):
  - `references/`: Documentation loaded on demand
  - `scripts/`: Helper executables (reviewed before running)
  - `assets/`: Templates, images, supporting files

## Versioning

This repository uses **semantic versioning** (MAJOR.MINOR.PATCH) in the `VERSION` file.

### Version Compatibility

The `coder-collab` tool enforces version compatibility:
- **Compatible**: Tool requires `1.0.0`, skills has `1.x.x` ✓
- **Incompatible**: Tool requires `1.x.x`, skills has `2.0.0` ✗

### When to Bump Versions

**PATCH (1.0.0 → 1.0.1)**:
- Fix typos or clarify existing instructions
- Add examples to existing skills
- Minor documentation improvements

**MINOR (1.0.0 → 1.1.0)**:
- Add new skills
- Add optional metadata to existing skills
- Add new references or scripts
- Backward-compatible improvements

**MAJOR (1.0.0 → 2.0.0)**:
- Remove or rename skills
- Change skill format or structure
- Breaking changes to skill API
- Requires corresponding `coder-collab` tool update

### Version Update Workflow

1. Make skill changes
2. Update `VERSION` file according to semver rules
3. Document changes in commit message
4. Human reviewer verifies version bump is appropriate
5. Merge to main

## Security Considerations

### Why Skills Are Separate

Skills are in a separate repository from the `coder-collab` tool to:
1. **Reduce attack surface**: Agent can't modify tool code and skills in same commit
2. **Simplify review**: Code reviews vs. content reviews are separate
3. **Enable different permissions**: Skills can have stricter controls

### Threat Model

**Skills influence agent behavior** through prompt injection. Malicious skill modifications could:
- Instruct agents to ignore security issues
- Bias code review toward accepting vulnerable code
- Exfiltrate information through misleading instructions

**Defense**: Human review of all skill changes before merging to canonical repository.

### Review Guidelines

When reviewing skill PRs:
1. **Check for subtle instruction changes** that could compromise security
2. **Verify VERSION bumps** match the scope of changes (semver compliance)
3. **Watch for social engineering** (skills that sound helpful but undermine safety)
4. **Review scripts carefully** before execution (in `scripts/` directories)
5. **Consider cross-skill interactions** (one skill loading another)

## Setup

Skills are loaded from the canonical repository location, typically:

```bash
# Symlink from coder-collab config to canonical skills repo
ln -s /home/ligon/Projects/coder-collab-skills ~/.coder-collab/skills
```

Configuration in `~/.coder-collab/config.yaml`:

```yaml
skills:
  - ~/.coder-collab/skills
```

## Contributing

### Adding a New Skill

1. Create skill directory: `mkdir my-skill`
2. Add `SKILL.md` with proper frontmatter
3. Add to `SKILLS.md` catalog
4. Update `VERSION` (minor bump)
5. Add tests in `tests/` if applicable
6. Submit PR for review

### Modifying Existing Skills

1. Make targeted changes
2. Test with `coder-collab` tool
3. Update `VERSION` appropriately
4. Document changes in commit message
5. Submit PR with clear rationale

## Testing

```bash
# Validate skill format and structure
pytest tests/

# Test skills with coder-collab tool
coder-collab collaborate <project> --task test-task
```

## License

See individual skills for licensing. Most skills are licensed under Apache-2.0.

## Related Repositories

- [Assistant](https://github.com/ligon/Assistant) - Main coder-collab tool repository
- Skills catalog maintained separately for security isolation

## Questions?

For issues or questions about:
- **Skill content**: Open issue in this repository
- **Tool integration**: Open issue in Assistant repository
- **Version compatibility**: Check `VERSION` file and tool requirements

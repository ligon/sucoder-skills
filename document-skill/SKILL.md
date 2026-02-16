---
name: document-skill
description: Use this skill to create or update skills for this workspace while staying aligned with Anthropic’s agent skill spec and our local conventions.
license: Apache-2.0
---

# Skill Authoring Guide

## When to Use
- You need to document a new capability for Coder or update an existing workspace skill.
- You want to share reusable context, scripts, or assets that should be discoverable by future sessions.
- You are verifying that a skill complies with Anthropic’s Agent Skills Spec before publishing.
- You plan to adapt material from shared repositories (e.g., `/tmp/skills`) and want local integration guidance.

## Philosophy
- Favor progressive disclosure: keep the opening summary short, surface detail only when it helps the user finish a task.
- Make instructions actionable—treat the skill like an onboarding packet another agent can follow without tribal knowledge.
- Prefer additive updates and keep skills interoperable across projects.

## Required Layout
1. **Location** – Place each skill in its own directory (e.g., `~/.coder-collab/skills/<name>`).
2. **Entrypoint** – Use a `SKILL.md` file with YAML frontmatter (`name`, `description`, `license`, optional `allowed-tools`, `metadata`). The `name` must match the directory.
3. **Body** – Provide clear procedures, checklists, and triggers. Move long references into separate files.
4. **Catalogs** – Add a `SKILLS.md` (or `SKILLS.org`) with short entries when the directory groups multiple skills.
5. **Resource directories** – Optional but encouraged:
   - `references/` for docs to load on demand.
   - `scripts/` for helper executables (never auto-run; mention suggested commands).
   - `assets/` for templates, media, or other output artifacts.

## Authoring Checklist
1. Define the scope: what tasks and knowledge does the skill cover?
2. Gather references, scripts, or assets and verify their paths.
3. Draft `SKILL.md` with metadata, overview, triggers, and structured sections.
4. Include headings for:
   - **Trigger** – when the agent should load the skill.
   - **Actions** – ordered procedures or commands.
   - **Pitfalls** – mistakes to avoid, escalation criteria, or fallback steps.
5. Populate `references/`, `scripts/`, and `assets/` as needed; reference them from the instructions.
6. Smoke-test the skill (`coder-collab collaborate … --task skill-smoke`) and confirm the prelude lists it and its resources.
7. Update the repository skills catalog and any mirror configuration so future sessions auto-discover it.

## Example Skeleton
```markdown
---
name: example-skill
description: Use this skill when …
license: Apache-2.0
---

# Example Skill

## Trigger
- Apply when …

## Steps
1. Command or checklist item.
2. …

## Additional Resources
- file:references/example.md
- Run `poetry run python scripts/demo.py`
```

## Maintenance
- Keep resource directories lean so generated summaries stay readable.
- Track non-obvious updates in a “Changelog” section with timestamps (e.g., `## <2025-11-07 Fri>`).
- Archive obsolete instructions instead of silent deletions—other agents may depend on prior behavior.

## Related Skills
- Load `skill-creator` for the full Anthropic agent skill creation workflow, packaging scripts, and validation tooling.

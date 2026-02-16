---
name: capture-attachments
description: Use this skill to capture new tasks/notes and manage attachments in Org documents.
license: Apache-2.0
---

# Capture and Attachments

## When to Use
- Recording tasks, notes, or meetings via capture templates.
- Attaching files or assets to Org headlines for documentation.
- Logging command sequences when attachments are added.

## Key Practices
1. **Capture Templates** — Capture entries using the configured templates in `~/.Misc/doom.org`. Apply the appropriate template (todo, diary, etc.) via `org-capture` or the scripts provided by maintainers.
2. **Refiling** — By default, captured items land in system-specific files (e.g., `~/Assistant/in.org`); refile them promptly to project-specific documents.
3. **Timestamps** — Ensure capture templates stamp entries with the current date `<YYYY-MM-DD Day>` to keep logs consistent.
4. **Attachments** — Store large files in designated directories (e.g., `docs/assets/`). Use org-attach or shell commands to move files, and note paths in handoffs.
5. **Scripts and Helpers** — Place helper scripts in `skills/orgmode/capture-attachments/scripts/` if capture automation is needed (empty for now—add as workflows solidify).

## House Rules
- See file:references/house-rules.org for default refile locations and attachment policy. Update as capture templates change.

## Related Skills
- `orgmode/dates-and-times` — For accurate timestamping in captured entries.
- `orgmode/todo-items` — Converting captured items into TODO workflows.
- `orgmode/drawers` — Storing capture metadata in drawers if needed.
- `orgmode/exporting` — Organizing attachments that need to be included in exports.

## Additional Resources
- file:references/house-rules.org — Capture and attachment policy.
- file:references/manual-links.org — Org manual chapters on capture templates and attachments.

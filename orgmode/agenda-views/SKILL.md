---
name: agenda-views
description: Use this skill to understand agenda configuration and custom views driven by workspace defaults.
license: Apache-2.0
---

# Agenda Views

## When to Use
- Reviewing scheduled tasks, deadlines, and custom agenda groupings.
- Confirming agenda settings after modifying TODO or effort properties.
- Documenting agenda-related commands in handoffs.

## Key Practices
1. **Standard Agenda** — Refresh the agenda with `C-c a a`. Diary integration is enabled (`org-agenda-include-diary t`), so calendars and journal entries appear alongside tasks.
2. **Skipping Scheduled** — The global TODO list hides entries already scheduled (`org-agenda-skip-scheduled-if-done t`). Keep this in mind when a task “disappears” after scheduling.
3. **Columns** — Agenda columns show item, TODO state, effort, priority, and tags. Use `C-c C-x C-c` inside the agenda to toggle column view if needed.
4. **Custom Views** — Any custom commands reside in `~/.Misc/doom.org`. If new persistent views are added, update that file and note them here.
5. **Integration with Other Skills** — Ensure effort estimates, TODO states, and capture entries feed into the agenda consistently.

## House Rules
- See file:references/house-rules.org for current agenda defaults (diary, skip scheduled, columns). Update it when configuration changes.

## Related Skills
- `orgmode/todo-items` — Agenda displays TODO states.
- `orgmode/dates-and-times` — Scheduling and deadlines drive agenda placement.
- `orgmode/effort-estimates` — Effort columns reflect the `EFFORT` property.
- `orgmode/capture-attachments` — Captured items appear in the agenda once refiled.

## Additional Resources
- file:references/house-rules.org — Agenda configuration policy.
- file:references/manual-links.org — Manual sections describing agenda usage and customization.

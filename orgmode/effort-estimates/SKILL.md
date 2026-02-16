---
name: effort-estimates
description: Use this skill to assign, manage, and review effort estimates on Org tasks.
license: Apache-2.0
---

# Effort Estimates

## When to Use
- Planning TODO items with expected durations.
- Displaying effort columns in agenda and column view.
- Comparing scheduled work with actual clocked time.

## Key Practices
1. **Set the EFFORT Property** — Position inside a headline and press `C-c C-x e` to set `EFFORT`. Enter durations as `H:MM` (e.g., `0:30`, `2:00`). Org stores the value in the `PROPERTIES` drawer.
2. **Predefine Values** — Add `#+PROPERTY: EFFORT_ALL 0:15 0:30 1:00 2:00` at the top of files (or configure `org-global-properties`) to cycle through standard durations.
3. **Agenda Columns** — Ensure agenda views display effort by setting `org-columns-default-format-for-agenda` (current default `%80ITEM %5TODO %7EFFORT %PRIORITY 100%TAGS`). Use `C-c C-x C-c` in buffers to review effort columns.
4. **Clock Comparison** — After clocking work (`org-clock`), run `org-clock-sum` or view clock reports to assess actual time against the `EFFORT` estimates. Adjust estimates when discrepancies persist.
5. **Reporting** — When handing off, note estimated vs. actual time if relevant; cite commands (e.g., `C-c C-x C-d`) used to produce summaries.

## House Rules
- Refer to file:references/house-rules.org for default value lists and agenda column expectations. Update it as policies evolve.

## Prompts for the Agent
- “Add a 30-minute `EFFORT` to these tasks so they appear in the agenda column.”
- “Populate `EFFORT_ALL` with common durations and realign column view.”
- “Compare clocked time with estimates and mention discrepancies in the handoff.”

## Related Skills
- `orgmode/todo-items` — Effort estimates complement TODO workflow states.
- `orgmode/properties-and-columns` — Manage property drawers and column formats.
- `orgmode/dates-and-times` — Coordinate scheduling and clocking with estimates.
- `orgmode/source-blocks` — Use source blocks to compute aggregate effort if needed.

## Additional Resources
- file:references/house-rules.org — Workspace defaults for effort properties.
- file:references/manual-links.org — Org manual sections on effort estimates, clocking, and column view.

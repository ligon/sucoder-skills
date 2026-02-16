---
name: dates-and-times
description: Use this skill to create timestamps, schedule tasks, manage deadlines, and track time according to our workspace norms.
license: Apache-2.0
---

# Dates and Times

## When to Use
- Scheduling tasks with `SCHEDULED` or `DEADLINE`.
- Creating recurring events, inactive timestamps, or timestamp ranges.
- Clocking work time and persisting clock data between sessions.

## Key Practices
1. **Timestamp Basics** — Use `<YYYY-MM-DD Day HH:MM>` for active timestamps, `[YYYY-MM-DD Day]` for inactive. Insert with `C-c .` or `C-c !`.
2. **Scheduling vs. Deadlines** — `SCHEDULED` indicates planned start; `DEADLINE` ensures agenda warnings. Remove completed scheduled tasks from global TODO (`org-agenda-skip-scheduled-if-done t`).
3. **Repeater Intervals** — Add `+1w`, `+2d`, etc., to create repeating tasks. Adjust with `S-UP/S-DOWN` at the timestamp.
4. **Range & Diary Sexp** — Use `--` between timestamps for ranges and `%%(...)` diary-style expressions for complex recurrences.
5. **Clocking** — Start/stop clocks with `C-c C-x C-i` / `C-c C-x C-o`. Persist state across sessions by enabling `org-clock-persist` and calling `(org-clock-persistence-insinuate)`.
6. **Agenda Integration** — Keep `org-agenda-include-diary t` so Emacs diary entries show up. Ensure effort estimates and tags complement scheduling.
7. **Capture Templates** — Templates should include timestamps (`SCHEDULED`, datetree targets, etc.) to keep new entries organized.

## House Rules
- See file:references/house-rules.org for default agenda and clocking preferences.
- Update the file when we change scheduling policies or capture defaults.

## Prompts for the Agent
- “Schedule this task for next Tuesday and add a weekly repeater.”
- “Mark these completed tasks with inactive timestamps to note when they finished.”
- “Start a clock before working on this item and stop it when done; ensure the LOGBOOK drawer captures the entry.”
- “Add a `DEADLINE` with a warning period so the agenda warns 3 days in advance.”

## Related Skills
- `orgmode` — Parent overview.
- `orgmode/todo-items` — Integrates with scheduling and deadlines to drive workflow.
- `orgmode/properties-and-columns` — Stores clock data and effort estimates in drawers/properties.
- `orgmode/hyperlinks` — Useful when linking to calendar entries or external references.

## Additional Resources
- file:references/house-rules.org — Local scheduling, diary, and clock defaults.
- file:references/manual-links.org — Org manual sections on timestamps, scheduling, and clocking.

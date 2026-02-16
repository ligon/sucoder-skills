---
name: drawers
description: Use this skill to manage Org drawers—LOGBOOK, PROPERTIES, NOTE, and custom drawers—while aligning with workspace conventions.
license: Apache-2.0
---

# Drawers

## When to Use
- Grouping metadata (properties, LOGBOOK entries) beneath a headline.
- Hiding scratch notes or exporter directives you don’t want in the main flow.
- Keeping clock data and state-change notes organized.

## Key Practices
1. **Placement** — Insert drawers immediately after the headline’s planning lines (`SCHEDULED`, `DEADLINE`). Use `C-c C-x p` or `C-u M-x org-insert-drawer` to create them.
2. **LOGBOOK** — Reserve `LOGBOOK` for clocks and TODO state notes. Our logging setup automatically stores entries there; leave it intact for history.
3. **PROPERTIES** — Store property key/value pairs in the `PROPERTIES` drawer. Keep property names uppercase for clarity and define `*_ALL` entries for allowed values.
4. **Custom Drawers** — Create descriptive drawers (`:NOTE:`, `:EXPORT:`) for scratch text or exporter hints. Close drawers with `:END:` and keep names uppercase per Org style.
5. **Reveal/Hide** — Use `org-cycle` to fold drawers. In exports, certain drawers (e.g., `LOGBOOK`) are ignored by default; ensure important notes live outside drawers if they must appear.
6. **House Style** — Maintain lowercase surrounding directives (`#+name:`) but keep drawer names uppercase. This keeps diffs readable and aligns with Org defaults.

## House Rules
- See file:references/house-rules.org for current drawer usage (LOGBOOK, PROPERTIES, note drawers). Update as needed.

## Prompts for the Agent
- “Move these scratch notes into a `:NOTE:` drawer to keep the headline clean.”
- “Ensure the LOGBOOK drawer remains below the heading and before body text.”
- “Create a PROPERTIES drawer and add the `OWNER` field with allowed values.”

## Related Skills
- `orgmode/properties-and-columns` — Properties stored inside drawers.
- `orgmode/todo-items` — Logging done/started state inside LOGBOOK.
- `orgmode/dates-and-times` — Clock data that populates LOGBOOK.

## Additional Resources
- file:references/house-rules.org — Drawer usage policy.
- file:references/manual-links.org — Manual sections on drawers and related features.

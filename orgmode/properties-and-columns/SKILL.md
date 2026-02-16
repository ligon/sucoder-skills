---
name: properties-and-columns
description: Use this skill to manage properties, inheritance, and column view layouts in Org files.
license: Apache-2.0
---

# Properties and Columns

## When to Use
- Adding metadata to tasks, notes, or project entries.
- Controlling property inheritance across subtrees or entire files.
- Displaying summary views via column view (both buffer-wide and in the agenda).

## Key Practices
1. **Property Syntax** — Place drawers immediately below the headline (after scheduling lines). Keys are case-insensitive, written as `:KEY:` followed by the value. Use `C-c C-x p` to set properties with completion.
2. **Allowed Values** — Define `PROPERTY_ALL` (either in the drawer or via `#+PROPERTY:`) to restrict values and enable cycling with `S-LEFT/RIGHT`.
3. **Inheritance** — Properties inherit down the outline when `org-use-property-inheritance` is non-nil. Exclude sensitive items (e.g., `crypt`) as needed.
4. **Global Defaults** — Use `#+PROPERTY:` at the top of a file or `org-global-properties` for repo-wide defaults.
5. **Special Properties** — Remember that pseudo-properties like `TODO`, `PRIORITY`, `CLOCKSUM`, etc., can be referenced in column view and queries but should not be set manually.
6. **Column View** — Activate with `C-c C-x C-c`. Customize columns via `#+COLUMNS:` lines or `org-columns-default-format`. Agenda uses `org-columns-default-format-for-agenda`; current default: `%80ITEM %5TODO  %7EFFORT %PRIORITY 100%TAGS`.

## House Rules
- See file:references/house-rules.org for workspace defaults (LOGBOOK drawer, agenda column format, inheritance exclusions). Update it as workflows evolve.

## Prompts for the Agent
- “Add an `EFFORT` property to these tasks so the agenda column layout stays useful.”
- “Define a `STATE_ALL` property so we can cycle through allowed project statuses.”
- “Filter inheritance to skip sensitive properties like `crypt` for this subtree.”
- “Set up a `#+COLUMNS:` line to display OWNER and DONE counts for this section.”

## Related Skills
- `orgmode` — Parent overview.
- `orgmode/todo-items` — Interacts closely with TODO state logging (properties record metadata inside LOGBOOK).
- `orgmode/tables` — Useful when exporting properties or column views as tables.

## Additional Resources
- file:references/house-rules.org — Local property and column defaults.
- file:references/manual-links.org — Org manual sections for properties, inheritance, and column view.

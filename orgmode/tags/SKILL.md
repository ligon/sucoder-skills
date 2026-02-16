---
name: tags
description: Use this skill to apply, inherit, and search tags while honoring our house conventions.
license: Apache-2.0
---

# Tags

## When to Use
- Categorizing tasks or notes with contexts (`:work:urgent:`) or locations (`:@home:`).
- Managing tag inheritance across large outlines or agenda files.
- Searching or filtering agenda views by tag combinations.

## Key Practices
1. **Basic Syntax** — Tags live at the end of headlines (`* Task :work:urgent:`). Press `C-c C-q` (or `C-c C-c` on a headline) to add/remove tags with completion.
2. **Inheritance** — Parent tags flow to children. Use `#+FILETAGS:` for file-wide defaults. Exclude sensitive tags (e.g., `crypt`) from inheritance via `org-tags-exclude-from-inheritance`.
3. **Definition Lists** — Set global or file-specific tag menus with `org-tag-alist` or `#+TAGS:`. Assign single-letter shortcuts for fast selection (e.g., `#+TAGS: @work(w) @home(h) project(p)`).
4. **Agenda Searches** — Control whether agenda views inherit tags by adjusting `org-agenda-use-tag-inheritance`. Disabling it can speed up large agenda queries.
5. **Tag Groups & Hierarchies** — Use tag groups when you want multiple tags to imply a broader category. Declare them in `org-tag-alist` or `#+TAGS:` (`:Parent:p`, `:Child:Parent`).
6. **Naming Conventions** — Prefer lowercase tags and `@context` prefixes for location or role-based tags. Keep names consistent across files to make tags searches reliable.

## House Rules
- See file:references/house-rules.org for local preferences (e.g., excluding `crypt` from inheritance). Update it as new patterns emerge.

## Prompts for the Agent
- “Apply `:project:` to the heading and ensure subheadings inherit it, except for anything tagged `crypt`.”
- “Update the `#+TAGS:` line to include this new context with a mnemonic shortcut.”
- “When searching the agenda, respect `org-agenda-use-tag-inheritance` so performance doesn’t suffer.”

## Related Skills
- `orgmode` — Parent overview.
- `orgmode/todo-items` — Combine tags with TODO keywords for workflow filtering.
- `orgmode/document-structure` — Useful when reorganizing tagged sections.

## Additional Resources
- file:references/house-rules.org — Workspace tag policies.
- file:references/manual-links.org — Org manual sections on tags, inheritance, and searching.

---
name: plain-lists
description: Use this skill to structure Org lists—bullets, description items, and checkboxes—while respecting workspace conventions.
license: Apache-2.0
---

# Plain Lists

## When to Use
- Writing bullet, numbered, or description lists inside paragraphs or sections.
- Building checklists that track progress before promoting items to full TODO entries.
- Nesting lists alongside code blocks or tables without breaking indentation.

## Key Practices
1. **Bullets & Numbering** — Use `-` for standard bullets, `1.` or `1)` for numbered lists. Org auto-increments numbers when you press `M-RET`.
2. **Description Lists** — Prefer `- Term :: Explanation` for definitions, settings, or option/value pairs—this keeps exports clean and matches our house style.
3. **Indentation** — Maintain two spaces for nested bullets and ensure code blocks under list items are indented consistently (usually four spaces after the bullet).
4. **Checkboxes** — Start the item with a bullet followed immediately by the checkbox marker, e.g., `- [ ]`, `- [X]`, or `- [-]`. Toggle with `C-c C-c`. Use checkboxes for short tasks; convert to TODO headlines when tracking history or scheduling.
5. **Auto Formatting** — `M-S-RET` inserts a new item with the same marker; `C-c C-c` realigns or fixes list markers; `C-c -` cycles bullet styles.
6. **Paragraph Continuation** — For multi-paragraph list items, indent subsequent lines to align under the text—not under the bullet marker.
7. **Exports** — Avoid using bold text as faux headings inside lists; promote to actual headlines or use description lists for emphasis.

## House Rules
- See file:references/house-rules.org for bullet and checkbox preferences. Update as necessary.

## Prompts for the Agent
- “Convert this bold colon list into proper description list syntax.”
- “Normalize nested indentation so every level uses two spaces.”
- “Toggle checkboxes to `[X]` only when the parent headline tracks completion.”

## Related Skills
- `orgmode` — Parent overview.
- `orgmode/markup` — Emphasis and block formatting inside list items.
- `orgmode/todo-items` — When checklists grow into full TODO workflows.

## Additional Resources
- file:references/house-rules.org — Workspace list conventions.
- file:references/manual-links.org — Org manual sections on list syntax and checkboxes.

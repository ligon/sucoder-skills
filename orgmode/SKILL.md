---
name: orgmode
description: Use this skill to recall workspace-friendly Org-mode authoring conventions and discover specialized sub-skills for deeper topics.
license: Apache-2.0
---

# Org-mode Authoring Overview

## When to Use
- You are creating a new `.org` document for this workspace.
- You are editing an existing Org file and need to confirm it follows formatting conventions.
- You are reviewing another contributor’s Org changes and want a quick checklist of expectations.

## Checklist
1. **Sectioning** — Use headline syntax (`*`, `**`, … followed by a space and title). Avoid ad-hoc bold headers.
2. **Math** — Wrap inline formulas with `\( … \)` and display math with `\[ … \]`; never use dollar signs. **Never begin a line inside display math with `+`, `-`, or `*`** (even after indentation): Org strips the leading whitespace and parses the bullet character as a plain-list item, silently breaking the `\[ … \]` fragment so it exports as escaped text and crashes LaTeX with `! Missing $`. Break the line *after* the operator, prefix the wrapped line with an empty group (`{} + ...`), or use a `\begin{equation}`/`\begin{align}` environment (immune, since Org never re-parses environments).
3. **Description Lists** — Prefer `- Label :: Details` over bold-with-colon patterns so LaTeX export stays clean.
4. **TODO Workflow** — Promote TODO entries to actual headings (e.g., `* TODO Review appendix`). Do not mimic TODOs with inline bold text.
5. **Character Set** — Stick to ASCII. Replace Unicode symbols with LaTeX macros (write `\alpha`, not `α`).
6. **Exceptions** — If you must violate a rule, leave a nearby comment explaining why so the next edit stays intentional.

## Tips
- Run a quick scan for stray Unicode by setting your editor to highlight non-ASCII characters.
- For long documents, place checklists or tables inside description lists to avoid LaTeX lint failures.
- If you need multi-state tasks beyond TODO/DONE, use Org’s built-in tags (e.g., `WAITING`, `NEXT`) as headline keywords.
- Multi-line display math is safest in a LaTeX environment (`\begin{equation}...\end{equation}`): Org passes environments through verbatim, whereas `\[ ... \]` fragments are re-parsed and break when a continuation line starts with a list bullet (`+`/`-`/`*`). If you keep `\[ ... \]`, break after the operator or prefix the wrapped line with `{}` (e.g. `{} + c`).

## Additional Resources
- file:references/rules_for_orgmode_markup.org — Full guidance with examples and rationale.

## Related Skills
- `orgmode/plain-lists` — Format bullets, description lists, and checkboxes cleanly.
- `orgmode/drawers` — Manage LOGBOOK, PROPERTIES, and custom drawers.
- `orgmode/blocks` — Insert example/quote/export blocks with house-style directives.
- `orgmode/source-blocks` — Execute and tangle Babel source blocks safely.
- `orgmode/rich-markup` — Detailed guidance on paragraphs, emphasis, math, and special symbols.
- `orgmode/hyperlinks` — Build internal/external links with descriptive IDs and export-friendly text.
- `orgmode/document-structure` — Headlines, visibility cycling, structure editing, and motion commands.
- `orgmode/markup` — Inline emphasis, directives, blocks, and house rules for rich content.
- `orgmode/tables` — Create readable tables, enforce naming conventions, and manage column widths.
- `orgmode/todo-items` — Manage workflow keywords, logging, and agenda visibility.
- `orgmode/tags` — Tag headlines, manage inheritance, and tune agenda searches.
- `orgmode/properties-and-columns` — Capture metadata with property drawers and customize column views.
- `orgmode/dates-and-times` — Schedule, add deadlines, and track time with timestamps and repeaters.
- `orgmode/effort-estimates` — Track planned durations and compare with clocked time.
- `orgmode/citations` — Insert org-cite references, configure export processors, and print bibliographies.
- `orgmode/exporting` — Run Emacs batch exports and manage output artifacts.
- `orgmode/capture-attachments` — Capture tasks/notes and manage attachments according to workspace policy.
- `orgmode/agenda-views` — Interpret agenda settings and custom views configured for this workspace.
- `orgmode/publishing` — Publish multi-file Org projects via org-publish.

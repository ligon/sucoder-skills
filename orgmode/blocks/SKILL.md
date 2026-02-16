---
name: blocks
description: Use this skill to insert and manage Org structural blocks (example, quote, export, LaTeX, etc.) in line with workspace conventions.
license: Apache-2.0
---

# Blocks

## When to Use
- Embedding example text, quotes, verse, or export-specific segments.
- Wrapping raw LaTeX/HTML snippets that shouldn’t be interpreted as regular text.
- Controlling how content is rendered in exports without promoting it to source blocks.

## Key Practices
1. **Insertion** — Use structure templates (`C-c C-,`) or `M-x org-insert-structure-template` to create blocks (`example`, `quote`, `center`, `verse`, `export`, etc.).
2. **Directive Style** — Keep block directives lowercase (`#+begin_example`, `#+end_example`, `#+begin_export latex`). This matches our house rules and improves diff readability.
3. **Spacing** — Leave blank lines before and after blocks (unless nested inside lists/tables where blank lines are forbidden).
4. **Naming & Captions** — When referencing blocks, add `#+name:` and optional `#+caption:` lines in lowercase just above the block.
5. **Export-Specific Blocks** — Use `#+begin_export <backend>` for backend-specific fragments (LaTeX, HTML). Remember these sections are skipped in other exports.
6. **Results & Literate Output** — Keep associated `#+results:` blocks lowercase and close to the source that generated them.

## House Rules
- See file:references/house-rules.org for our lowercase directive policy and spacing requirements.

## Prompts for the Agent
- “Convert this fenced code snippet into an `example` block with lowercase directives.”
- “Add a caption and name to this block so exports can reference it.”
- “Ensure there’s a blank line before and after each block outside of lists.”

## Related Skills
- `orgmode/markup` — Inline formatting surrounding blocks.
- `orgmode/plain-lists` — Handling blocks nested inside list items.
- `orgmode/properties-and-columns` — Sometimes used alongside blocks for metadata.
- `orgmode/source-blocks` — (Upcoming) for executable source code blocks.

## Additional Resources
- file:references/house-rules.org — Block styling policy.
- file:references/manual-links.org — Org manual sections about blocks and structure templates.

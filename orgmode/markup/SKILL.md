---
name: markup
description: Use this skill to apply Org markup consistently, observe house rules, and know where to find richer syntax examples.
license: Apache-2.0
---

# Markup for Rich Contents

## When to Use
- Styling text (emphasis, code spans, links) or inserting special symbols.
- Embedding example/source blocks, results drawers, or named elements.
- Preparing content for export where LaTeX compatibility matters.

## Key Practices
1. **Emphasis & Monospace** — Wrap bold/italic/verbatim using `*bold*`, `/italics/`, `=code=`, `~verbatim~`. Avoid nested emphasis that breaks export; prefer `#+begin_src` blocks for multi-line code samples.
2. **Math** — Inline math must use `\( … \)` and display math uses `\[ … \]`. Never use `$...$` / `$$...$$`; exporters and diff tooling stay happier with the LaTeX-style delimiters.
3. **Directives** — Keep structural keywords lowercase (`#+name:`, `#+begin_src`, `#+results:`). It reads better in diffs and matches our house style; Org treats keywords case-insensitively so this is safe.
4. **Special Blocks** — Choose `#+begin_example` for literal text, `#+begin_src lang` for executable code, `#+begin_quote` for quotations, etc. Leave a blank line before and after blocks unless inside list/table contexts that forbid it.
5. **Entities & ASCII** — Use LaTeX commands (`\alpha`, `\ndash`) or Org entities (`\nbsp{}`) instead of raw Unicode. Keeps exports working with our pdflatex pipeline.
6. **Tables of Contents & Links** — When exporting, insert `#+toc: headlines <n>` explicitly instead of relying on defaults; keep link descriptions concise and meaningful.

## House Rules
- See file:references/house-rules.org for the evolving list of local preferences (math delimiters, lowercase directives, ASCII discipline). Append to that file as new quirks arise.
- For code execution semantics (header arguments, tangling, results handling), defer to the upcoming `orgmode/source-blocks` skill.

## Prompts for the Agent
- “Ensure every `#+BEGIN_SRC` usage is lowercase and surrounded by a blank line unless embedded in a list.”
- “We’re adding math snippets—convert any `$...$` into `\(...\)` or `\[...\]` before committing.”
- “Check this doc for stray Unicode; replace with LaTeX macros so export to PDF keeps working.”

## Related Skills
- `orgmode` — Parent overview and general authoring checklist.
- `orgmode/document-structure` — Outline manipulation, visibility, and navigation tools.
- Future: `orgmode/source-blocks` (to cover execution, results drawers, tangling).

## Additional Resources
- file:../references/rules_for_orgmode_markup.org — Original workspace guidance on Org markup.
- file:references/house-rules.org — Editable house-style addendum.
- file:references/manual-links.org — Direct links into the Org manual’s markup chapters.
- file:../rich-markup/SKILL.md — Detailed instructions for paragraphs, emphasis, math, and special symbols.

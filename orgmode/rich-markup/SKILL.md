---
name: rich-markup
description: Use this skill to format paragraphs, emphasis, math, and special symbols cleanly while respecting workspace style.
license: Apache-2.0
---

# Markup for Rich Contents

## When to Use
- Styling paragraphs with quoted, centered, or verse blocks.
- Applying emphasis (bold/italic/code) and toggling pretty entities.
- Writing math in ASCII-safe LaTeX form and inserting special symbols.

## Key Practices
1. **Paragraphs & Blocks** — Separate paragraphs with blank lines. Use `#+begin_quote`, `#+begin_center`, or `#+begin_verse` (lowercase) for formatted blocks and add blank lines around them.
2. **Emphasis** — Apply `*bold*`, `/italic/`, `_underline_`, `=code=`, and `~verbatim~` where appropriate. Use `C-c C-x C-f` (`org-emphasize`) to insert markers, and avoid nesting emphasis that confuses exporters.
3. **Subscripts/Superscripts** — Use ASCII-friendly `^`/`_` syntax, e.g., `R_{sun}`. Configure `#+OPTIONS: ^:{}` if you need curly notation. Toggle pretty display with `C-c C-x \`.
4. **Math Delimiters** — Inline math goes in `\( ... \)`; display math in `\[ ... \]`. Never use `$...$` or `$$...$$`. 
5.  **Prefer \LaTeX markup to unicode** —  Keep LaTeX commands ASCII-only (e.g., `\mu`, `\Sigma`).
6. **Special Symbols** — Type `\` + letters and press `M-TAB` to insert Org entities (`\alpha`, `\to`). Avoid pasting Unicode characters; rely on LaTeX commands for portability.
7. **Line Breaks** — Use `\\` for manual breaks within a paragraph. For poetry or preformatted text, wrap content in a `verse` block.
8. **Display Math** — Do *not* put extra vertical whitespace before and after display math unless you really mean to end a paragraph.
9. **Leading Operators in Display Math** — Never begin a line inside `\[ ... \]` (or `\( ... \)`) with `+`, `-`, or `*`, even after indentation. Org strips the leading whitespace and reads the bullet character as a plain-list item, which breaks the math fragment: on export `\[` becomes literal text, the body is escaped (`\{`, `\textsuperscript{}`), a stray `\item` is inserted, and LaTeX aborts with `! Missing $`. (This is distinct from inline `+...+` strike-through; see references/house-rules.org.) Three fixes, in order of preference: (a) break the line *after* the operator so it trails the previous line; (b) start the wrapped line with an empty group, `{} + c`, which stops Org's list parsing and is a harmless no-op in LaTeX (it also forces binary-operator spacing); (c) use a `\begin{equation}`/`\begin{align}` environment, which Org never re-parses.

```text
   \[ a = b + c \]          % operator mid-line -- fine

   \[ a = b                 % BREAKS: continuation line starts with "+"
      + c \]

   \[ a = b                 % OK: empty group guards the bullet
      {} + c \]

   \[ a = b +               % OK: operator trails the previous line
      c \]
```

## House Rules
- See file:references/house-rules.org for our math delimiter and ASCII policies. Update it as conventions evolve.

## Prompts for the Agent
- “Replace all `$...$` inline math with `\(...\)` and ensure display math uses `\[...\]`.”
- “Convert pasted Unicode Greek letters to LaTeX commands (`\alpha`, `\beta`, …).”
- “Wrap this quotation in a `#+begin_quote` block with blank lines around it.”

## Related Skills
- `orgmode/blocks` — Structural blocks for quotes, verse, and center layout.
- `orgmode/markup` — High-level checklist referencing markup norms.
- `orgmode/source-blocks` — For executable code blocks; keep math in rich-markup.

## Additional Resources
- file:references/house-rules.org — Workspace-specific markup constraints.
- file:references/manual-links.org — Org manual chapters for rich content formatting.

---
name: tables
description: Use this skill to create, format, and maintain Org tables that follow workspace naming and width conventions.
license: Apache-2.0
---

# Tables

## When to Use
- Capturing structured data that benefits from column alignment or spreadsheet formulas.
- Updating table contents prior to export (HTML, LaTeX) where layout matters.
- Reviewing tables to ensure they comply with local naming and width rules.

## Key Practices
1. **Insert & Align** — Start a table with `|` and Org will auto-align on `TAB`. Use `C-c |` to convert regions to tables or `M-S-RET` to insert rows.
2. **Naming** — Prepend every table with a lowercase directive: `#+name: tab:<slug>`. This enables formulas, exports, and cross-references while matching house style.
3. **Captions & Descriptions** — Add `#+caption:` (and optionally `#+label:`) directly above tables for export-friendly titles.
4. **Column Alignment** — Use alignment cookies in the separator line (e.g., `|---+---|`) and press `TAB` to re-align. For numeric columns, add `<r>` or `<c>` to the alignment row as needed.
5. **Width Control** — Keep tables readable within ~120 columns. Add column width cookies (e.g., `<10>`) in the separator row to shrink wide columns, or split oversized tables.
6. **Spreadsheet Features** — Use `C-c =` to edit field formulas, `C-c C-c` to recalc, and the `@row` / `$col` addressing syntax for references. Store global formulas in `#+TBLFM:` lines.
7. **Sorting & Transforming** — `C-c ^` sorts rows; `C-c |` converts to/from CSV-style text. For complex transformations, consider exporting the table to a dedicated script.

## House Rules
- See file:references/house-rules.org for naming, width, and export conventions. Update that file to capture new patterns.

## Prompts for the Agent
- “Ensure every table has a `#+name: tab:<slug>` before committing.”
- “This table looks wide—add `<width>` cookies so the display fits in a 120-character window.”
- “Regenerate alignment with `TAB` after editing formulas or inserting new columns.”

## Related Skills
- `orgmode` — Parent overview for general Org authoring.
- `orgmode/document-structure` — Manipulate headings if you need to reposition tables.
- `orgmode/markup` — Guidance on surrounding captions, descriptions, and inline formatting.

## Additional Resources
- file:references/house-rules.org — Workspace table preferences.
- file:references/manual-links.org — Direct links to Org manual sections on tables and spreadsheet features.

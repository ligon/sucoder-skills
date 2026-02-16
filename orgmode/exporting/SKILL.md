---
name: exporting
description: Use this skill to export Org documents to PDF/HTML/Markdown via Emacs batch commands and project scripts.
license: Apache-2.0
---

# Exporting

## When to Use
- Generating PDFs, HTML, or Markdown from Org manuscripts or documentation.
- Automating exports (e.g., for paper drafts) without opening Emacs interactively.
- Sharing reproducible commands/scripts with maintainers.

## Key Practices
1. **Batch Emacs** — Run exports with Emacs in batch mode so they can be reproduced. Example:
   ```bash
   emacs --batch manuscript.org -l ~/.emacs.d/init.el -f org-latex-export-to-pdf
   ```
   Use `org-html-export-to-html`, `org-md-export-to-markdown`, etc., for other formats.
2. **Scripts** — Invoke `skills/orgmode/exporting/scripts/export-pdf.sh` when you want a standard export harness. Update the script if the repo uses a custom init file.
3. **Document Options** — Capture export settings inside the Org file (`#+OPTIONS:`, `#+TITLE:`, `#+AUTHOR:`, `#+cite_export:`) so batch commands stay simple.
4. **Assets & Paths** — Ensure figures, bibliography, and LaTeX dependencies are available; keep paths relative to the Org file so the export runs on other machines.
5. **Cleaning Output** — Remove auxiliary LaTeX artifacts if they aren’t needed for review (`rm *.aux *.log`). Leave PDFs/HTML in the repository root unless the project specifies an output directory.
6. **Citations/Bibliography** — Confirm that export processors match the citation skill (`orgmode/citations`) so references render correctly.

## House Rules
- See file:references/house-rules.org for default commands, target directories, and flag conventions.
- Extend `scripts/` with additional helpers (HTML, Markdown) as workflows evolve.

## Prompts for the Agent
- “Add a `#+OPTIONS:` block so batch exports don’t need extra flags.”
- “Confirm `export-pdf.sh` produces the latest draft and list the command in the handoff.”
- “Trim auxiliary files after export to keep diffs clean.”

## Related Skills
- `orgmode/citations` — Align export processors with citation styles.
- `orgmode/source-blocks` — Tangle or execute code that feeds into exported documents.
- `orgmode/rich-markup` — Ensure math/emphasis render correctly in exported formats.
- `orgmode/dates-and-times` — Log export runs in handoff notes with timestamps.

## Additional Resources
- file:references/house-rules.org — Workspace export conventions.
- file:references/manual-links.org — Org manual chapters on exporting.
- file:scripts/export-pdf.sh — Ready-to-run batch script (assumes Emacs installed).

---
name: hyperlinks
description: Use this skill to insert, style, and maintain Org hyperlinks, including internal targets and custom link types, while following workspace conventions.
license: Apache-2.0
---

# Hyperlinks

## When to Use
- Creating cross-references within a document or across project files.
- Linking to external resources while keeping exports readable.
- Maintaining anchors (`CUSTOM_ID`, targets) when reorganizing sections.

## Key Practices
1. **Basic Syntax** — Links follow `[[type:target][description]]`. Omit the description only when the target itself is human-readable.
2. **Internal Links** — To link to a heading, add `:CUSTOM_ID:` properties and reference with `[[#custom-id]]`. For inline targets, use descriptive radio targets (`<<sec:overview>>`) and link via `[[sec:overview]]`.
3. **External Links** — Wrap URLs with a short description (`[[https://orgmode.org][Org manual]]`). Avoid bare links in prose.
4. **File Links** — Use `[[file:path/to/file.org::*Heading]]` for anchored references. Keep paths relative and lowercase the link keyword (`file:`) per house style.
5. **Targets & IDs** — Prefer stable identifiers (`CUSTOM_ID` or named radio targets) over automatically generated ones so future reorganizations are painless.
6. **Custom Link Types** — Define workspace link styles via `org-link-set-parameters` when you need consistent handling (e.g., `org://ticket/<id>`). Document new link types in the house rules file.
7. **Export Tips** — For footnotes or references, combine links with captions or descriptive text rather than duplicating the URL. Adjust HTML/LaTeX attributes with `#+ATTR_HTML:` or `#+ATTR_LATEX:` rather than inline markup.

## House Rules
- See file:references/house-rules.org for local preferences (naming, descriptive IDs, lowercase keywords). Update it as new patterns emerge.

## Prompts for the Agent
- “Ensure every cross-reference uses `CUSTOM_ID` or a named target, not the default radio target from Org.”
- “Wrap these external URLs with readable descriptions before export.”
- “Convert `[[File:...]]` to lowercase `[[file:...]]` and drop redundant relative prefixes.”

## Related Skills
- `orgmode` — Parent overview.
- `orgmode/document-structure` — Useful when you’re reorganizing headings and need to preserve IDs.
- `orgmode/markup` — For inline formatting around links, including emphasis and special blocks.

## Additional Resources
- file:references/house-rules.org — Workspace guidance on link naming and targets.
- file:references/manual-links.org — Quick access to Org manual chapters on hyperlinks and custom link types.

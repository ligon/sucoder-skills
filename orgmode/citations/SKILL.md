---
name: citations
description: Use this skill to manage org-cite citations, bibliographies, and export processors the same way you handle academic writing.
license: Apache-2.0
---

# Citation Handling

## When to Use
- Inserting citations, footnotes, or textual references in Org documents.
- Configuring bibliography databases and export processors.
- Printing bibliographies or per-section reference lists.

## Key Practices
1. **Insert with org-cite** — Use `C-c C-@` (or `org-cite-insert`) to add citations such as `[cite:@townsend94]`, `[cite/t:@arrow-debreu54]`, or `[cite/u:@ligon-etal02]`. Avoid raw LaTeX commands; stick to org-cite syntax so all exporters behave.
2. **Bibliography Setup** — Ensure documents include `#+bibliography: ~/bibtex/main.bib` (and any project-specific `.bib` files). Doom config already sets `org-cite-global-bibliography` to `~/bibtex/main.bib`, so most files just need overrides for additional sources.
3. **Export Processors** — Rely on the configured processors:
   - Markdown/HTML → CSL `chicago-fullnote-bibliography.csl`
   - LaTeX → biblatex with APA options (`apa,backend=biber,sortcites=ynt`)
   - Everything else → CSL full-note
   Confirm `org-cite-export-processors` matches the Doom configuration before exporting.
4. **Custom Styles** — Use the custom `full` style (`[cite/full:@key]`) mapped to biblatex’s `fullcite` for long-form footnotes. Add other styles to `org-cite-biblatex-styles` as needed.
5. **Printing Bibliographies** — Add `#+print_bibliography:` where you want references rendered. For LaTeX export, include `\addbibresource{main.bib}` in headers if not already present.
6. **Complementary Tools** — `citar` is configured as the citation picker; use its interface to search Zotero/BibTeX entries and insert org-cite links quickly.

## House Rules
- See file:references/house-rules.org for bibliography locations, processor defaults, and syntax expectations. Update if citation workflows change.

## Prompts for the Agent
- “Replace raw `\cite{}` commands with org-cite syntax (`[cite:@key]`).”
- “Add `#+bibliography:` entries and ensure `#+print_bibliography:` appears near the end.”
- “Confirm the document uses the chicago full-note processors and includes the custom `full` style when invoking `[cite/full:@key]`.”

## Related Skills
- `orgmode/rich-markup` — For surrounding LaTeX/math contexts in academic text.
- `orgmode/source-blocks` — Useful when generating bibliography statistics or cite lists via code blocks.
- `orgmode/properties-and-columns` — When storing metadata about references in property drawers.

## Additional Resources
- file:references/house-rules.org — Workspace conventions for citations.
- file:references/manual-links.org — Org manual sections describing org-cite usage and export processors.

---
name: source-blocks
description: Use this skill to insert, execute, and tangle Org Babel source blocks while honoring workspace safety and style conventions.
license: Apache-2.0
---

# Source Blocks

## When to Use
- Running literate programming snippets inside Org files.
- Tangling code into standalone scripts or modules.
- Capturing results from exploratory computations directly in documentation.

## Key Practices
1. **Directive Style** — Use lowercase directives: `#+name:`, `#+begin_src lang ...`, `#+end_src`, `#+results:`. Place optional `#+name:` immediately above the block.
2. **Header Arguments** — Specify execution intent explicitly (`:results output`, `:exports both`, `:tangle path`, `:session`, `:noweb`). Default to `:eval never-export` or `:eval no` when blocks shouldn’t run automatically.
3. **Spacing & Context** — Leave a blank line before and after blocks unless embedded in tables/lists. Keep surrounding text readable.
4. **Tangling Discipline** — Provide clear tangle targets (`:tangle src/demo.py`) or disable tangling with `:tangle no`. Use temporary paths when the block is scratch work; never rely on implicit tangling.
5. **Results Handling** — Keep `#+results:` blocks lowercase and near the generating block. Use `:results value` for structured data, `:results output` for logs. Clean obsolete results before handoff.
6. **Safety & Languages** — Execute only whitelisted languages (Python, shell, etc.) and avoid enabling new languages without approval. Prefer `:dir` and `:var` headers over hard-coded `cd` commands.
7. **Sessions & Reproducibility** — Use `:session` only when interactive state is required; otherwise default to stateless blocks. Record seeds or environment variables inside the block when results depend on randomness.

## House Rules
- See file:references/house-rules.org for directive style, spacing, tangling expectations, and evaluation policies.

## Prompts for the Agent
- “Rename `#+BEGIN_SRC` to lowercase and add explicit `:results output` and `:exports code` headers.”
- “Add `:tangle scripts/example.py` and ensure the block writes to that path.”
- “Convert this scratch block to `:eval never-export` so it doesn’t execute during export.”

## Related Skills
- `orgmode/blocks` — Structural (non-source) blocks.
- `orgmode/markup` — Formatting around source blocks and results.
- `orgmode/properties-and-columns` — Recording evaluation metadata in drawers.
- `orgmode/dates-and-times` — Logging when source blocks run (e.g., via `LOGBOOK`).

## Additional Resources
- file:references/house-rules.org — Local execution and style policy.
- file:references/manual-links.org — Relevant Org manual sections on Babel usage.

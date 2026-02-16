---
name: document-structure
description: Use this skill to edit Org headlines, control visibility, and reshape outlines without breaking workspace conventions.
license: Apache-2.0
---

# Document Structure

## When to Use
- Organizing or reorganizing headings within an Org document.
- Tuning the initial visibility or cycling settings before sharing a file.
- Moving, cloning, or sorting subtrees while keeping TODO states and metadata intact.

## Key Practices
1. **Headlines** — Start at column 0 with one or more stars plus a space. Keep blank lines between subtrees to improve folded views.
2. **Visibility Cycling** — Use `TAB` on a headline for local cycling, `S-TAB` for global cycling. `C-u C-u TAB` restores startup visibility.
3. **Startup Visibility** — Add `#+STARTUP: overview|content|showall|show<n>levels` at the top of the file, or set `VISIBILITY` properties per entry.
4. **Safe Editing** — Leave `org-fold-catch-invisible-edits` enabled so edits do not touch hidden text unexpectedly.
5. **Motion** — `C-c C-n` / `C-c C-p` move between headings; `C-c C-f` / `C-c C-b` stay on the same level; `C-c C-j` jumps via `org-goto`.
6. **Structure Editing** — `M-RET` inserts a sibling, `C-RET` respects subtree content, `M-LEFT/RIGHT` promote/demote, and `M-UP/DOWN` reorder subtrees.
7. **Subtree Operations** — Use `C-c C-x C-w/M-w/C-y` to cut, copy, and paste whole trees with automatic level adjustment; `C-c ^` sorts children.
8. **Sparse Trees** — Create focused views with sparse-tree commands (e.g., `C-c / t` for TODO keywords) instead of manual folding.

## Prompts for the Agent
- “We’re about to restructure this outline—ensure headings follow the star syntax and leave blank lines for folded views.”
- “Before handing off, set `#+STARTUP:` so the reader sees either an overview or the content we want.”
- “Use `M-LEFT/M-RIGHT` to promote or demote these TODO items rather than editing the stars directly.”

## Related Skills
- `orgmode` — Parent skill with general authoring guidance and other Org subtopics.
- Load the Org manual chapter for deeper reference (see below).

## Additional Resources
- file:references/manual-links.org — Pointers into the upstream Org manual for document-structure tasks.

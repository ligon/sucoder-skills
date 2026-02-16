---
name: todo-items
description: Use this skill to manage TODO keywords, logging, and agenda visibility in line with our workflow.
license: Apache-2.0
---

# TODO Items

## When to Use
- Promoting or demoting tasks through the TODO workflow (`TODO → NEXT → … → DONE`).
- Configuring logging behavior when tasks change state.
- Adjusting agenda views to match the house conventions.

## Key Practices
1. **Keyword Sequence** — Default states: `TODO`, `NEXT`, `DELEGATE`, `WAITING`, `PLAN` → `DONE`, `MOOT`, `SOMEDAY`. Use the mnemonic shortcuts (`t`, `n`, `l`, `w`, `p`, `d`, `m`, `s`) during `C-c C-t`.
2. **Logging** — Keep `org-log-done` and `org-log-into-drawer` enabled so completions and notes land inside a `LOGBOOK`. `DELEGATE` and `WAITING` prompt for notes to capture ownership and resumption.
3. **Agenda Hygiene** — Skip tasks already scheduled when viewing the global TODO list (set `org-agenda-skip-scheduled-if-done t`). Use effort estimates (`EFFORT` property) so agenda columns stay meaningful.
4. **State Changes** — Use `C-u C-c C-t` to timestamp state transitions when needed (see manual references). Consider `org-todo-state-tags-triggers` if you want automatic tag toggles.
5. **Recurring/Follow-up Tasks** — For repeating items, rely on scheduled with repeater intervals. Use `SOMEDAY` for parking future tasks without cluttering active agendas.
6. **Capture Templates** — Ensure templates create TODO entries with the appropriate initial state (`* TODO ...`) and clocking behavior if you want `LOGBOOK` entries.

## House Rules
- See file:references/house-rules.org for our current keyword set, logging requirements, and agenda tweaks. Update this file whenever workflows change.

## Prompts for the Agent
- “Change these tasks from TODO to NEXT only if they’re ready to work—otherwise leave them as TODO.”
- “When delegating, ensure `DELEGATE` is set and add a note about who owns the follow-up.”
- “Verify that completed tasks recorded timestamps inside the LOGBOOK drawer.”
- “Skip scheduled items from the global TODO list by setting `org-agenda-skip-scheduled-if-done`.”

## Related Skills
- `orgmode` — Parent overview.
- `orgmode/document-structure` — For reorganizing task hierarchies or refiling.
- `orgmode/markup` — Use when adding notes or formatting within TODO drawers.
- `orgmode/hyperlinks` — Helpful if you reference tasks across files via internal links.

## Additional Resources
- file:references/house-rules.org — Workspace workflow details.
- file:references/manual-links.org — Org manual sections on TODO management, logging, and workflow extensions.

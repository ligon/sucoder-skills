---
name: publishing
description: Use this skill to publish multi-file Org projects with org-publish.
license: Apache-2.0
---

# Publishing

## When to Use
- Exporting a collection of Org files (documentation, website) with a single command.
- Defining project trees via `org-publish-project-alist`.
- Sharing instructions for maintainers to regenerate published content.

## Key Practices
1. **Configure Project** — Define `org-publish-project-alist` entries pointing at source directories and output destinations. Document the configuration (README or skill house rules) so others can reproduce it.
2. **Run Publishing** — Use Emacs batch commands or interactive `org-publish-all` to build the site. Example batch command:
   ```bash
   emacs --batch -l ~/.emacs.d/init.el \
     --eval \"(require 'ox-publish)\" \
     --eval \"(org-publish-all t)\"
   ```
   Adjust `-l` and project names as needed.
3. **Output Management** — Publish into a dedicated directory (`docs/_site`, `public/`, etc.). Clean or ignore build artifacts if they shouldn’t be tracked.
4. **Links & Assets** — Ensure relative links resolve under the publish directory. Use `org-publish` link replacement features instead of hard-coding absolute paths.
5. **Document Workflow** — Record the exact commands or scripts used to publish so future maintainers can regenerate the site.

## House Rules
- See file:references/house-rules.org for current project alist conventions and output directories. Update as publishing pipelines change.

## Related Skills
- `orgmode/exporting` — Run single-file exports.
- `orgmode/source-blocks` — Tangle or evaluate code that supports pages.
- `orgmode/citations` / `orgmode/rich-markup` — Ensure content renders correctly before publishing.

## Additional Resources
- file:references/house-rules.org — Publishing policy.
- file:references/manual-links.org — Org manual sections on publishing configuration and commands.

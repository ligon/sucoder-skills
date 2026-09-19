---
name: semantic-line-breaks
description: Use this skill to lay out Org prose one sentence per line (semantic line breaks). Covers sentence boundaries, the abbreviations that are not boundaries, structures that stay atomic (headlines, tables, math, citations, code), and when to leave existing paragraphs alone.
license: Apache-2.0
---

# Semantic Line Breaks (One Sentence Per Line)

## When to Use
- Writing new prose in an `.org` file: paper sections, working notes, referee responses, correspondence.
- Editing a paragraph in an existing Org document (see key practice 10 before reflowing anything you are *not* editing).
- Reviewing an Org diff and deciding whether a line-layout change is warranted.

## Why
Break lines at sentence boundaries and a diff shows which sentence changed instead of which fill-column rewrap happened. Redlines land on one line each, `git blame` resolves to a sentence, and conflicts shrink to the sentences two people both touched. The rendered output does not change: Org joins consecutive non-blank lines into a single paragraph, separated by a space, so the exported PDF or HTML is identical either way.

## Key Practices
1. **Break after sentence terminators** — End a line after `.`, `?`, or `!` when it genuinely closes a sentence. Nothing else ends a line. Do *not* break after commas or semicolons; a long subordinated sentence stays on one long line, however wide.
2. **Not every period ends a sentence** — This is the rule that goes wrong most often. Do not break after: `e.g.`, `i.e.`, `cf.`, `et al.`, `vs.`, `viz.`, `ibid.`; structural references such as `Fig. 2`, `Tab. 1`, `Sec. 3`, `Prop. 1`, `Thm. 4`, `eq. (7)`, `Ch. 5`, `p. 17`, `no. 3`; honorifics and initials (`Dr.`, `Prof.`, `E. A. Ligon`); initialisms (`U.S.`, `U.K.`); decimals and versions (`0.5`, `Python 3.11`); and ellipses (`...`). The working test: break only when what follows begins a new independent sentence. When in doubt, leave the line unbroken — a missed break is cosmetic, a wrong break garbles the sentence. Common cases are listed here; the appendable register is `file:references/examples.org`.
3. **Colons** — Break after a colon only when the clauses on both sides are complete, independent thoughts (rough gauge: five or more words each). Never break after the `::` of a description list, nor after a colon introducing a short phrase, a definition, or a label.
4. **A newline is not a paragraph break** — Org opens a new paragraph only at a *blank* line. One sentence per line therefore changes the source and not the output. It follows that the standing prohibition on blank lines around display math still binds (`orgmode/rich-markup` key practice 8): resume on the next line, never after a blank one.
5. **Atomic lines — never split these** —
   - Headlines (`* Heading`), whatever punctuation they contain.
   - Keywords and directives: `#+title:`, `#+caption:`, `#+name:`, `#+options:`, and friends.
   - Drawers: `:PROPERTIES:` … `:END:`, LOGBOOK entries, timestamps.
   - Table rows (`| … |`). A row is one line; Org's aligner owns it.
   - The interior of `#+begin_src` and `#+begin_example` blocks. Leave code and literal text byte-for-byte; this is a prose rule.
   - `#+begin_verse` blocks, where newlines are already semantic and `\\` is doing real work.
   - Citations (`[cite:@key]`, `[cite/t:@key]`) and footnote references (`[fn:1]`). Treat them as single tokens and never break on punctuation inside them.
   - `#+begin_quote` is the exception that *does* take one sentence per line: it holds prose.
6. **Lists** — The first sentence of an item goes on the bullet line (`- First sentence.`). Later sentences in the same item start their own line, indented to the item's *text* column rather than under the bullet marker (`orgmode/plain-lists` key practice 6). Description lists keep the tag and first sentence together: `- Term :: First sentence.`
7. **Inline math is prose** — Never break inside `\( … \)`, and break after it only when a sentence terminator follows.
8. **Display math is one atomic unit** — Put a `\[ … \]` fragment or a `\begin{equation}` / `\begin{align}` environment on its own line or lines. When the equation falls mid-sentence, resume the sentence on the line directly below the closing delimiter. Start a new line for a new sentence only when the equation itself closed the previous one with a period. Do not break a long `\[ … \]` across lines merely because this skill encourages breaks: a continuation line beginning with `+`, `-`, or `*` is parsed as a list bullet and silently destroys the fragment (`orgmode/SKILL.md` key practice 2).
9. **Footnote definitions** — `[fn:1] First sentence.` on the definition line; subsequent sentences on their own lines.
10. **Scope: do not reflow what you are not editing** — Apply this layout to new prose and to paragraphs you are already changing. Leave untouched paragraphs alone, and never convert a whole file in a commit that also changes its content. Most older Org prose in this workspace is fill-column wrapped at roughly 72 characters, and a bulk reflow buries the real edit in an unreviewable diff. If a file deserves wholesale conversion, make it a commit that changes nothing else.
11. **Sentence spacing becomes moot** — Within a paragraph the newline replaces it, so the two-spaces-after-a-period habit visible in older fill-wrapped prose simply disappears as paragraphs are reflowed. Nothing to enforce either way.

## Example
```org
* Model Formulation
Consider the optimization problem for an agent facing the budget set \(\mathcal{B}\).
We define the objective function as
\begin{equation}
  \max_{c \in \mathcal{B}} \sum_{t=0}^{\infty} \beta^t u(c_t),
\end{equation}
where \(u(\cdot)\) satisfies the standard Inada conditions (see, e.g., [cite:@stokey-lucas89]).
Does the value function admit a unique fixed point?
The answer is affirmative: the contraction mapping theorem applies directly under bounded returns.
```

Three things to notice. The sentence interrupted by the equation resumes on the line below `\end{equation}` with no blank line, so it stays one paragraph. The `e.g.` inside the parenthetical is not a break point, and neither is the citation's internal punctuation. The final colon is not a break point either: `The answer is affirmative` is four words, short of an independent clause worth its own line.

## House Rules
- New Org prose uses one sentence per line. Existing prose converts when it is edited, not on sight (key practice 10).
- The math delimiters remain `\( … \)` and `\[ … \]` as always; this skill never introduces `$ … $` or `$$ … $$`, and prefers a `\begin{equation}` environment to a `#+begin_equation` special block.
- Append newly discovered non-terminators to the register in `file:references/examples.org` rather than rediscovering them.

## Prompts for the Agent
- "Reflow this section to one sentence per line, leaving the other sections untouched."
- "Check this file for lines holding more than one sentence, and for breaks after `e.g.` or `Fig. 3`."
- "Rewrite this paragraph in the Ligon voice and lay it out one sentence per line."

## Related Skills
- `orgmode` — Parent checklist; the standing one-line version of this rule.
- `orgmode/rich-markup` — Math delimiters, and `\\` for a break that survives export (a different thing entirely from these newlines).
- `orgmode/plain-lists` — Indentation for the continuation lines of a list item.
- `orgmode/citations` — org-cite syntax for the tokens key practice 5 keeps atomic.
- `ligon-voice`, `research-writer`, `technical-editor` — The prose skills whose output this layout governs.

## Additional Resources
- file:references/examples.org — Worked before/after conversions and the appendable abbreviation register. The file is itself written one sentence per line.

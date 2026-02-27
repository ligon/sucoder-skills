---
name: ligon-voice
description: Use this skill to draft or revise research prose---papers, working notes, referee responses, and editorial correspondence---in the Ligon academic voice. This skill should be used when the user asks for help writing, editing, or polishing research-oriented text.
license: Apache-2.0
---

# Ligon Voice

Adopt the writing voice of a senior academic economist: technically rigorous
yet approachable, authoritative yet self-aware.  The voice mixes three
registers freely---technical economics, development-policy vocabulary, and
plain conversational English---and uses contractions, dry humor, and high
sentence-length variance as deliberate stylistic tools.

## When to Use

Apply this skill when:
- Drafting or editing academic research papers
- Writing working notes or internal research memos
- Composing referee responses or editorial correspondence
- Polishing prose that should sound like it belongs in a development-economics
  journal submission

Do **not** apply when writing code comments, commit messages, README files, or
casual chat.

## Workflow

1. **Quick edits and short passages** --- use the Key Rules and Quick-Reference
   Checklist below.  These capture the highest-impact habits and fit within the
   context budget.
2. **Extended drafting or revision** --- load the full style guide for detailed
   rules, examples, and improvement strategies:
   `file:references/style-guide.org`

## Key Rules

These are the most distinctive features of the voice, distilled from the full
guide.  Apply all of them by default.

### Sentence architecture
- Vary sentence length deliberately: alternate long, subordinated sentences
  (40--60 words) with short, punchy resets (4--15 words).
- After any passage exceeding ~50 words of continuous qualification, follow
  with a sentence under 15 words that reorients the reader.
- Impose a soft ceiling of ~50 words per sentence.  Violate only when the
  structure is genuinely parallel and each clause is short.
- For lists of 3--4 conceptually parallel claims, use a single
  semicolon-joined sentence.  Beyond 4 items, break into two sentences or use
  an actual list.

### Lexicon
- Use contractions freely ("it's," "can't," "doesn't," "we've").  This is
  the single most distinctive lexical feature.
- Use technical vocabulary without apology when it is precise; surround it
  with plain, conversational connecting prose.  Never stack jargon without
  bridging it with everyday language.
- Hedge empirical claims; be direct about theory.  One hedge per claim---never
  hedge the hedge.  If the evidence is thin, say so directly.

### Tone
- Write as a senior professor explaining to a smart colleague.  Build
  intuition before formalism; explain what was just shown and why it matters.
- Treat prior work with genuine respect.  Show its limits through concrete
  consequences, not dismissal.  Let absurdity speak for itself.
- Use "we" for formal prose; "I" for editorial letters and genuinely personal
  judgments.  Let the directness of the working-note voice survive into the
  final draft.

### Rhetoric and structure
- Open with what is known, then pivot to what is missing.  State the
  punchline in the first paragraph, then build the case.
- Use one rhetorical question per section opening, max.  Follow it
  immediately with the beginning of an answer.
- At most one parenthetical per sentence.  Promote extras to their own
  clause, an em-dash aside, or a footnote.
- At the top of any derivation spanning more than a page, add a single
  orienting sentence ("We need three results to establish the main
  proposition").

### Humor and figurative language
- Humor is dry and arises from the material.  Never signal that you are being
  funny.  At most one exclamation mark per paper.
- Deploy at most 1--2 vivid metaphors per paper, borrowed from adjacent
  domains (finance, manufacturing, physical effort).  Let each work in a
  single clause, then return to precision.

## Quick-Reference Checklist

| Feature              | Do                                                           | Don't                                                       |
|----------------------+--------------------------------------------------------------+-------------------------------------------------------------|
| Sentence length      | Vary widely (15--60+ words); follow complex with simple      | Write uniformly long or uniformly short sentences           |
| Sentence ceiling     | Soft cap at ~50 words; break semicolon-lists beyond 4 items  | Let clause-stacking obscure the main verb                   |
| Contractions         | Use freely ("it's," "can't," "doesn't")                     | Avoid entirely, or overuse to the point of slang            |
| Technical vocabulary | Use precisely; bridge with plain-English prose               | Stack jargon without explanation                            |
| Hedging              | One hedge per claim; be direct about theory                  | Accumulate hedges across a paragraph                        |
| Metaphor             | 1--2 per paper; vivid, slightly wry, from adjacent domains   | Extended conceits; similes; mixed metaphors                 |
| Humor                | Understated, from the material; never flagged                | Broad jokes; forced cleverness; sarcasm                     |
| Rhetorical questions | One per section opening, max                                 | Mid-paragraph; in clusters; without an immediate answer     |
| Prior literature     | Acknowledge respectfully, then show limits through results   | Dismiss; strawman; ignore                                   |
| First person         | "We" for formal; "I" for editorial/personal judgment         | "One" as a systematic substitute; passive voice as default  |
| Openings             | State the punchline in paragraph 1, then build the case      | Delay the contribution behind a full page of setup          |
| Parentheticals       | At most one per sentence; quick factual glosses              | Multiple nested parentheticals; entire arguments in parens  |
| Signposting          | Orienting sentence at the top of long derivations            | Multi-page arguments with no sub-signposts                  |
| Register in revision | Preserve the notes-voice directness in the final draft       | Formalize away clarity present in the working draft         |
| Exclamation marks    | At most once per paper, for genuine emphasis                 | As decoration or enthusiasm                                 |

## Related Skills

- `file:../orgmode/SKILL.md` --- Org-mode authoring conventions (much of the
  writing happens in Org files).

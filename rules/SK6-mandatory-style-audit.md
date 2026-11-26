## Mandatory Style Audit (GATE — applies to ALL tex edits)

**Before presenting or committing ANY new or modified tex content, Claude MUST run a sentence-level style audit.** This is not optional, not triggered by the user, and not limited to full section drafts — it applies to every edit, including paragraph-level changes, subsection additions, and overview rewrites.

The audit checks every changed sentence against the Mechanical Gate below. Specifically, scan for and fix:

0. **Mechanical gate (below) — run FIRST, with its greps.** Em-dashes (`---`, `—`, ` -- `) are BANNED. Antithesis/mirror flourishes ("X, not Y"; "whatever it is called"), editorializing closers ("the saving is the point", "is not real"), vacuous intensifiers ("in effect", "at its core"), rule-of-three decoration, throat-clearing openers ("Moreover", "Notably"), banned/pompous/fancy words, and content-free openers ("In this paper, we…") are BANNED. Target the plain, short, declarative register. Do NOT report the audit as passed without running its Part C greps.
1. **Negation-first constructions**: "not X" or "rather than X" where the sentence should assert what something IS. Reframe positively.
2. **Throat-clearing**: "We address this problem by", "To address this issue", "In order to", "It should be noted that", "Note that". Delete and lead with the action.
3. **Hedging**: "can potentially", "can be expected to", "may help reduce", "it is possible that". Replace with assertive voice ("produces", "reduces", "achieves"), except for a claim that genuinely outruns its evidence: hedge that one.
4. **Generic adjectives**: "significant", "substantial", "highly desirable", "novel", "robust", "comprehensive". Replace with specific numbers or delete.
5. **Sentence length**: Flag any sentence exceeding 40 words. Split or compress.
6. **Passive voice**: "accuracy was achieved by X" → "X achieves". "Experiments were conducted on X" → "We evaluate on X". Active voice everywhere — no exceptions, including methods and evaluation. Run the M11 passive-detection grep (Part C below) in this base gate; fix or justify every hit.
7. **Missing citations**: Technical claims restated from other sections must carry forward their citations (Principle 14: technical claims require citations).
8. **Rendered artifact (the Artifact Gate below)**: any edit that adds or changes a float, caption, or table also runs the artifact gate — compile, grep the `.log` for overfull boxes and undefined references, then render every changed page to an image and inspect its floats for clipping/overflow, reused-float refit, legibility, color-as-only-channel, caption terseness, and placement. A source-only pass is half a gate; a figure or table is not audited until it is rendered and looked at.

**Process**: After writing, (a) run the Mechanical Gate's Part C greps and fix every hit, then (b) read the changed text line by line for the items above. Report a summary table of violations found and fixed (category, count), INCLUDING the grep counts (em-dashes, flourishes) — not just "audited". Never claim the audit passed on a mental pass alone. Then (c), for any edit that adds or changes a float, caption, or table, run the **artifact gate** (below): compile, grep the `.log` for overfull boxes and undefined references, and render every changed page to an image and inspect its floats. Only text that survives (a) + (b), and (c) where it applies, with the grep output and rendered-page evidence pasted, is presented or committed.

This gate is SEPARATE from and IN ADDITION TO the section checklists.

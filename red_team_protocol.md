# Independent Adversarial Red-Team Protocol

> Why this exists: the de-AI mechanical gate and the style audit are run by the SAME agent that wrote the
> prose, which then self-reports "passed." Self-audit rationalizes its own phrasing, and the mechanical grep
> is skipped or its output never shown. Result: AI-sounding, inaccessible, and illogical text ships anyway.
> This protocol makes review INDEPENDENT and EVIDENCE-GATED.

## When
On every section draft or non-trivial rewrite: AFTER the author runs the de-AI mechanical gate + style
audit, and BEFORE the text is shown to the user or committed.

## Three gates — text must survive all three
1. **WRITE** — the author agent produces the draft.
2. **MECHANICAL GATE** — run ALL of the Mechanical Gate's Part C greps. PASTE the raw output (hit counts
   + lines). Zero unjustified hits to proceed. "Audited" without pasted output is INVALID.
3. **INDEPENDENT RED-TEAM** — a SEPARATE reviewer that did NOT write the text. It:
@rules/RT1-reviewer-instructions.md

   This gate also includes the four lens passes of `author_profile/gate_semantic.md` S29, each run
   by its own fresh reviewer in addition to the reviewer above.

## Evidence rule
The grep output + the red-team findings ARE the audit record. A section is "clean" only when the red-team
returns zero surviving findings WITH the pasted grep evidence. Never report clean on a mental pass.

## How to run the independent reviewer
Spawn a subagent (or a clearly separated reviewer persona) whose ONLY input is the drafted text + these
checklists + the paper's controlling idea. It must NOT see the author's self-assessment. In a multi-agent
workflow this is a distinct verify stage; interactively it is a fresh Agent that reviews and returns findings.
The author then fixes every finding and the cycle repeats until the reviewer returns clean.

A finding that asks for more detail gets the S33 test: does the reader need this in the
article to trust the result? If so, the detail goes into the article. If not, it moves to the cut file.

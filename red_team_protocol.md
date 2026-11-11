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
2. **MECHANICAL GATE** — run ALL of `gate_mechanical.md` Part C. PASTE the raw output (hit counts
   + lines). Zero unjustified hits to proceed. "Audited" without pasted output is INVALID.
3. **INDEPENDENT RED-TEAM** — a SEPARATE reviewer that did NOT write the text. It:
   - re-runs the `gate_mechanical.md` greps itself (does not trust the author's report): em-dashes,
     antithesis, intensifiers, banned/pompous/fancy words, passive voice (zero tolerance), wordiness;
   - applies `author_profile/gate_semantic.md` (S1–S31) with a FRESH-READER lens: "a venue reader
     who has never seen this paper — flag every undefined term, every claim not tied to the thesis, every
     illogical jump" — plus lexical + decomposition consistency, non-duplication, mappability/grounding,
     honest positioning, and directness (deliver the noun);
   - hunts the four failure classes explicitly: AI-sounding, inaccessible, incoherent, illogical;
   - REFUSES to pass until clean, returning a findings list — not a yes/no. Each finding cites the
     exact **rule ID** it violates (`M#` from `gate_mechanical.md` or `S#` from `gate_semantic.md`),
     plus line and concrete fix. The rule ID is the provenance: it makes every fix traceable to the
     specific rule in the ledger.

   This gate also includes the four lens passes of `author_profile/gate_semantic.md` S29, each run
   by its own fresh reviewer in addition to the reviewer above. When the project defines review agents
   in `.claude/agents/`, the work of this gate is split across them instead: a facts reviewer and the
   four lens reviewers, which together do everything listed above.

## Evidence rule
The grep output + the red-team findings ARE the audit record. A section is "clean" only when the red-team
returns zero surviving findings WITH the pasted grep evidence. Never report clean on a mental pass.

## How to run the independent reviewer
Spawn a subagent (or a clearly separated reviewer persona) whose ONLY input is the drafted text + these
checklists + the paper's controlling idea. It must NOT see the author's self-assessment. In a multi-agent
workflow this is a distinct verify stage; interactively it is a fresh Agent that reviews and returns findings.
The author then runs review rounds:
1. Rebuild the paper, then launch fresh reviewers, Sonnet at high effort: every gate 3 reviewer.
   Wait until all have reported before changing anything.
2. Judge each finding: fix the ones that hold, and record why any is declined.
3. Rebuild the paper, then tell each reviewer, for each of its findings, whether it was fixed and,
   if not, why. Ask it to re-read only the changed parts of the text it reviewed. It checks only its
   own findings.
4. If a reviewer does not accept, return to step 2 for its findings.
5. When all accept and a Sonnet round had any CRITICAL or MAJOR finding, start again at step 1.
6. When a Sonnet round had none, run the same round with fresh Opus reviewers at high effort.
7. When an Opus round has no CRITICAL or MAJOR finding, the review is done. If it has any, fix them
   (steps 2–4), then ask the user whether to run a second Opus round.
Report each round's token cost. The author may use Opus instead of Sonnet when Sonnet reviews waste
time, and tells the user.

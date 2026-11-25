# Mechanical Gate — the single greppable style audit

> The ONE place for every mechanically detectable style rule. Merges what used to live in three
> separate grep scripts (de-AI, Elements-of-Style, hardening) plus the base voice profile's
> banned-word lists. Run it on every `.tex` edit in the base gate, and again in the red-team/loop
> pass. **Report the grep counts, not "audited."** Every hit is either fixed or explicitly
> justified before the edit is reported done. A mental pass is not a run.

This gate holds the checks a regex can catch. Reader-judgment checks (define-before-use,
followability, coherence, grounding) are the Semantic Gate's S rules, run by the reviewers. Positive
"what to write instead" guidance is the Craft Reference, loaded for drafting.

---

## Part A — Banned constructions (fix every hit)

Each rule states the ban, then a wrong→right example.

@../rules/M1-em-dashes.md

@../rules/M2-antithesis.md

@../rules/M3-editorializing-closers.md

@../rules/M4-vacuous-intensifiers.md

@../rules/M5-banned-adjectives.md

@../rules/M6-throat-clearing-openers.md

@../rules/M7-rule-of-three.md

@../rules/M8-grandiose-setups.md

@../rules/M9-metaphor-filler.md

@../rules/M10-hype-verbs.md

@../rules/M11-passive-voice.md

@../rules/M12-needless-words.md

@../rules/M13-weak-qualifiers.md

@../rules/M14-coined-adverbs.md

@../rules/M15-exclamation-marks.md

@../rules/M16-pompous-words.md

@../rules/M17-fancy-verbs.md

@../rules/M18-content-free-openers.md

---

@../rules/M19-precision-word-pairs.md

---

@../rules/M20-grep-script.md

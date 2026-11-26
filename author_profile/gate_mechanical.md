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

@../rules/M1-em-dashes.yml

@../rules/M2-antithesis.yml

@../rules/M3-editorializing-closers.yml

@../rules/M4-vacuous-intensifiers.yml

@../rules/M5-banned-adjectives.yml

@../rules/M6-throat-clearing-openers.yml

@../rules/M7-rule-of-three.yml

@../rules/M8-grandiose-setups.yml

@../rules/M9-metaphor-filler.yml

@../rules/M10-hype-verbs.yml

@../rules/M11-passive-voice.yml

@../rules/M12-needless-words.yml

@../rules/M13-weak-qualifiers.yml

@../rules/M14-coined-adverbs.yml

@../rules/M15-exclamation-marks.yml

@../rules/M16-pompous-words.yml

@../rules/M17-fancy-verbs.yml

@../rules/M18-content-free-openers.yml

---

@../rules/M19-precision-word-pairs.yml

---

## Part C — The grep script (RUN THIS; do not eyeball)

@@grep-script

Report the per-category hit counts in the audit summary. "Clean" means every hit fixed or
justified, with the counts shown.

# Semantic Gate — the reader-judgment style audit

> The failures a grep cannot catch: undefined terms, thesis drift, unparseable sentences,
> ungrounded numbers, inconsistent naming, dishonest positioning. These are what reviewers
> actually reject on. Run this in the red-team and `/loop` passes, with a FRESH-READER lens — a
> reviewer who has not seen the paper and did not write the text. Each item returns findings
> (category, line, why it matters to a reader), not a yes/no; the author decides the fix.
> Severity: MAJOR = reviewer-visible confusion;
> CRITICAL = structural or logical incoherence.

Greppable checks live in `gate_mechanical.md`; positive drafting guidance in `craft_reference.md`.

---

## Group 1 — Accessibility and followability

@../rules/S1-define-before-use.yml#reviewers

@../rules/S2-term-introduction-order.yml#reviewers

@../rules/S3-spell-out-acronyms.yml#reviewers

@../rules/S4-recursive-followability.yml#reviewers

@../rules/S5-parse-accessibility.yml#reviewers

@../rules/S6-gloss-once.yml#reviewers

---

## Group 2 — Coherence and consistency

@../rules/S7-thesis-tie.yml#reviewers

@../rules/S8-lexical-consistency.yml#reviewers

@../rules/S9-term-map-decomposition.yml#reviewers

@../rules/S10-non-duplication.yml#reviewers

@../rules/S11-referent-scan.yml#reviewers

---

## Group 3 — Directness

@../rules/S12-deliver-the-noun.yml#reviewers

@../rules/S13-no-gloss-pile-ups.yml#reviewers

@../rules/S14-dangling-modifiers.yml#reviewers

---

## Group 4 — Rigor and grounding

@../rules/S15-no-orphan-numbers.yml#reviewers

@../rules/S16-ground-critiques.yml#reviewers

@../rules/S17-data-integrity.yml#reviewers

@../rules/S18-hedge-scan.yml#reviewers

@../rules/S32-citation-authenticity.yml#reviewers

---

## Group 5 — Structure and framing

@../rules/S19-requirement-closure.yml#reviewers

@../rules/S20-positives-first.yml#reviewers

@../rules/S21-honest-positioning.yml#reviewers

@../rules/S22-enabling-system-capability.yml#reviewers

@../rules/S23-claim-first-headings.yml#reviewers

@../rules/S24-table-for-walls.yml#reviewers

@../rules/S33-validation-detail-to-cut-file.yml#reviewers

---

## Group 6 — Figures (verify by looking, not by checklist)

@../rules/S25-no-text-panels.yml#reviewers

@../rules/S26-numbers-on-structure.yml#reviewers

@../rules/S27-right-figure-right-section.yml#reviewers

@../rules/S28-legibility-by-inspection.yml#reviewers

---

## Group 7 — Process: red-team lenses and the closure gate

@../rules/S29-distinct-lenses.md

@../rules/S30-venue-calibration.yml#reviewers

@../rules/S31-closure-gate.md

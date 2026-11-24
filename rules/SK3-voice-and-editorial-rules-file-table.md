## Voice and Editorial Rules

Claude MUST read these files from this skill's directory. They contain the detailed rules with examples.

| File | What it controls |
|---|---|
| `author_profile/editorial_principles.md` | 14 cross-paper principles with evidence (introduction-twice, named-over-vague, what→why→so-what headings, compress-after-expanding, etc.) |
| `author_profile/craft_reference.md` | **How to write (the positive layer).** Sentence-level style (~21-word mean, claim-first, active voice, named-over-vague, no filler), composition craft, and three registers: base/terse, conceptual/position, warm/narrative. Read while drafting a paragraph. |
| `author_profile/gate_mechanical.md` | **The single mechanical grep gate (M1–M18).** Em-dashes, antithesis, intensifiers, banned + pompous + fancy verbs, throat-clearing, passive voice, wordiness, qualifiers, term-drift — one grep script. Run on every tex edit; the passive-voice scan also runs in the base gate. |
| `author_profile/gate_semantic.md` | **The single reader-judgment gate (every S-numbered item in the file).** Define-before-use, followability, parse-accessibility, thesis-tie, lexical + decomposition consistency, non-duplication, rigor/grounding, honest positioning, figures, and the **closure gate**. Runs in the red-team/loop pass. |
| `author_profile/gate_artifact.md` | **The rendered-artifact gate (A1–A9).** Compile + grep the `.log` (overfull boxes, undefined refs, missing assets), then render + inspect every changed page for clipped/overflowing floats, reused-float refit, legibility, color-as-only-channel, caption terseness, and placement. Catches what a source-only pass cannot see. Run on every edit that touches a float, caption, or table. |
| `author_profile/compression_patterns.md` | 7 compression operations with before/after examples and quantitative benchmarks |
| `author_profile/rhetorical_moves.md` | Cross-section move sequences for introduction (6 moves), design (5 moves), evaluation (6 moves), related work (3 moves) |
| `author_profile/intervention_types.md` | 7 types of advisor interventions — use this to simulate advisor feedback on drafts |
| `red_team_protocol.md` | **Independent adversarial red-team** (evidence-gated): after the mechanical audit, a reviewer that did NOT write the text re-runs `gate_mechanical.md` and applies `gate_semantic.md`, and must return CLEAN before text ships. |
| `loop_mode.md` | Resumable `/loop` audit-and-fix protocol: a disk-backed ledger, one section per iteration, self-terminating when clean. |

## Mode 3: Critique — "Does this figure serve the paper?"

### Step 1: Load Context

Read all of:
- The `figure_spec.md` for this figure
- The generated figure (image or compiled PDF)
- The paper's `project_context.md`
- `figure_templates/venue_styles.md` for formatting standards

### Step 2: Run Five Checks

#### Check 1: Claim Alignment

- Does the figure support the specific claim listed in the spec's "Paper claim supported" field?
- Could a reader understand the claim from the figure alone (with caption)?
- Does the figure show anything that contradicts or weakens the claim?
- **Verdict**: PASS / REVISE (with specific fix)

#### Check 2: Completeness

- Are all components from the spec present in the figure?
- Are all connections shown?
- Are all groupings visible?
- Are labels legible and correctly spelled?
- Is the key contribution component visually prominent?
- **Verdict**: PASS / REVISE (list missing elements)

#### Check 3: Venue Formatting

- Does the figure fit the target column width without rescaling below legibility?
- Is text at least 8pt at print size?
- Is the background white?
- Are colors from the approved palette?
- Would the figure be readable in grayscale?
- **Verdict**: PASS / REVISE (list violations)

#### Check 4: Design Principles

- **Data-ink ratio** (Tufte): Is every visual element encoding information? Remove decorative borders, background fills, and chrome that don't carry meaning.
- **Self-containment**: Can a reader understand the high-level flow without reading the paper body?
- **Simplicity**: Could any component be removed without losing information? If yes, remove it.
- **Consistency**: Does the style match other figures in this paper? (Same fonts, colors, line weights, node shapes.)
- **Verdict**: PASS / REVISE (list violations)

#### Check 5: Caption Quality

- Is the caption interpretive (states what the figure shows and why it matters)?
- Is it claim-first (the takeaway leads, details follow)?
- Does it follow craft_reference.md rules (no hedging, no filler adjectives, active voice)?
- Is it self-contained enough for a skim-reader?
- **Verdict**: PASS / REVISE (suggest rewrite)

### Step 3: Produce Critique Report

Present results as a table:

| Check | Verdict | Details |
|-------|---------|---------|
| Claim alignment | PASS/REVISE | ... |
| Completeness | PASS/REVISE | ... |
| Venue formatting | PASS/REVISE | ... |
| Design principles | PASS/REVISE | ... |
| Caption quality | PASS/REVISE | ... |

**Overall verdict:**
- **PASS** — all checks pass. The figure is ready for inclusion.
- **REVISE** — one or more checks failed. List the specific action items and suggest re-running generate mode with updated spec/prompt.

### Step 4: Update the Spec

After critique, update the `figure_spec.md`:
- Set "Critique passed: yes/no"
- Record iteration notes (what needs to change for the next version)

---

## Cross-Figure Consistency

When a paper has multiple non-data figures, enforce consistency across all of them:

1. **Color semantics**: If blue represents "our system" in Figure 1, it must represent "our system" in all figures. Document the color-to-meaning mapping in the first `figure_spec.md` and reference it from all others.
2. **Node shapes**: Consistent shape vocabulary across figures (rectangles for processing stages, cylinders for data stores, diamonds for decision points).
3. **Font and line weight**: Identical across all figures — use the shared styles from `venue_styles.md`.
4. **Naming**: The same component must have the same label in every figure. If the architecture overview calls it "Encoder Stage," the component detail figure must also call it "Encoder Stage."
5. **Level of detail**: Figures at the same level of abstraction should have similar visual complexity. An architecture overview shouldn't be more detailed than a component detail figure.

When critiquing any figure after the first, check consistency against all previously critiqued figures.

<!-- Not included by any mode since 2026-11-25: each paragraph points at a figure mode for one stage; the one line each stage's mode needs is in modes/architecture.md (via SK11), modes/draft-design.md and modes/integrate.md. Kept for the installed figure_synthesis_guide.md. -->
## Integration with the Paper Pipeline

This guide connects to the paper-writing pipeline at three points:

**Stage 2 (Architecture):** When building the section architecture table, classify each figure from "Key Figures Needed" as data (→ `/viz`) or non-data (→ `/paper-writing figure spec`). Run `figure spec` for all non-data figures during this stage.

**Stage 3 (Section Drafts):** When drafting the Design section, the architecture overview figure should already exist. Design Move 3 (Component Architecture) uses it as structural scaffolding — each subsection corresponds to a component in the overview figure. If the figure doesn't exist yet, run `/paper-writing figure generate` before drafting.

**Stage 4 (Integration):** During the cross-section consistency pass, run `/paper-writing figure critique` on all non-data figures. Check visual balance, claim alignment, and cross-figure consistency.

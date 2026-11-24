# Figure Synthesis Guide: Non-Data Figures for Systems/Networking Papers

@rules/FG1-overview.md

---

@rules/FG2-spec.md

---

@rules/FG3-generate.md

---

@rules/FG4-critique.md

---

## Integration with the Paper Pipeline

This guide connects to the paper-writing pipeline at three points:

**Stage 2 (Architecture):** When building the section architecture table, classify each figure from "Key Figures Needed" as data (→ `/viz`) or non-data (→ spec mode here). Run spec mode for all non-data figures during this stage.

**Stage 3 (Section Drafts):** When drafting the Design section, the architecture overview figure should already exist. Design Move 3 (Component Architecture) uses it as structural scaffolding — each subsection corresponds to a component in the overview figure. If the figure doesn't exist yet, generate it before drafting.

**Stage 4 (Integration):** During the cross-section consistency pass, run critique mode on all non-data figures. Check visual balance, claim alignment, and cross-figure consistency.

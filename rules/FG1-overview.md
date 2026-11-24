This guide helps synthesize **conceptual figures** — architecture diagrams, pipeline illustrations, comparison schematics, and other non-data figures. It does NOT handle data figures (CDFs, bar charts, scatter plots, heatmaps) — those go through the [data-visualization-skill](https://github.com/SNL-UCSB/data-visualization-skill) via `/viz`.

**The boundary:** If a figure requires experimental data to render, it goes through `/viz`. If it illustrates structure, flow, or concepts, it comes here.

## Modes

- `/paper-writing figure spec` — Classify non-data figures, walk through archetype-specific questions, produce a `figure_spec.md`
- `/paper-writing figure generate` — Route to AI prompt or TikZ, produce the figure
- `/paper-writing figure critique` — Review against claims, venue formatting, design principles

## Choosing a Mode

When the user asks for help with a non-data figure, assess where they are:

| State | Suggested mode |
|-------|---------------|
| Has `project_context.md` but no `figure_spec.md` for this figure | **Spec** |
| Has a `figure_spec.md` but no generated figure | **Generate** |
| Has a generated figure and wants feedback | **Critique** |
| Not sure what figures they need | **Spec** (start from project_context.md's Key Figures Needed) |

If no `project_context.md` exists, stop. The student must run the brainstorming workflow first (`/paper-writing` → brainstorming). Figures cannot be designed in a vacuum — they serve claims, and claims live in the project context.

---

## Seven Figure Archetypes

Every non-data figure in a systems/networking paper fits one of these archetypes. The archetype determines which questions to ask in spec mode and which generation backend to use.

| Archetype | What it shows | Typical section | Default backend |
|-----------|--------------|-----------------|-----------------|
| **Architecture Overview** | Full system pipeline, end-to-end flow with named stages, phase groupings | §3 Design (opener), full-width | AI image generation |
| **Pipeline / Process Flow** | Sequential transformation of data through stages, with intermediate representations | §3 Design (subsection) | TikZ |
| **Component Detail** | Internal structure of one pipeline stage, sub-components and their interactions | §3 Design (subsection) | TikZ |
| **Concept Illustration** | Abstract concept made concrete — before/after, spatial analogy, visual metaphor | §2 Background / Motivation | AI image generation |
| **Comparison Schematic** | Why approach A fails and approach B works, side-by-side structural contrast | §1 or §2 Motivation, §3 Design justification | AI image generation |
| **Taxonomy / Classification** | Hierarchical or matrix organization of categories, positioning the paper | §5 Related Work, §2 Background | TikZ |
| **Deployment / System Diagram** | Physical or logical infrastructure topology, how the system runs in practice | §4 Evaluation setup, §2 Background | AI image generation |

**The student can override the default backend.** If they want TikZ for an architecture overview (for precise control) or AI generation for a taxonomy (for visual richness), respect that choice.

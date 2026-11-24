### "I need a non-data figure (architecture diagram, pipeline illustration, etc.)"
1. Load the paper's `project_context.md`
2. Read the files for `/paper-writing figure <step>` (see **Modes** in SKILL.md) and the relevant files in `figure_templates/`
3. Classify the figure by archetype (architecture overview, pipeline flow, component detail, concept illustration, comparison schematic, taxonomy, deployment diagram)
4. Select the generation backend: AI image generation (for visually rich figures like architecture overviews and concept illustrations) or TikZ (for precise structural figures like pipeline flows and taxonomy matrices). The guide has defaults per archetype, but the student can override.
5. Run spec mode — walk through archetype-specific questions to produce a `figure_spec.md`
6. Run generate mode — assemble an AI prompt or TikZ code, produce the figure
7. Run critique mode — check against claims, venue formatting, and design principles, and enforce caption terseness (G7: a bold takeaway plus at most one clause; flag captions over ~3 lines), and verify legibility by inspecting the rendered image (a checklist-green figure can still be an illegible mess)
8. **NOTE**: Data figures (CDFs, scatter plots, bar charts, heatmaps) should go through `/viz`, not through figure synthesis

### "I need a non-data figure (architecture diagram, pipeline illustration, etc.)"
1. Load the paper's `project_context.md`
2. Invoke `/paper-writing figure <step>` (spec, generate or critique); its files name the templates in `figure_templates/` to use
3. Classify the figure by archetype (architecture overview, pipeline flow, component detail, concept illustration, comparison schematic, taxonomy, deployment diagram)
4. Select the generation backend: AI image generation (for visually rich figures like architecture overviews and concept illustrations) or TikZ (for precise structural figures like pipeline flows and taxonomy matrices). The guide has defaults per archetype, but the author can override.
5. `/paper-writing figure spec` — walk through archetype-specific questions to produce a `figure_spec.md`
6. `/paper-writing figure generate` — assemble an AI prompt or TikZ code, produce the figure
7. `/paper-writing figure critique` — check against claims, venue formatting, and design principles, and enforce caption terseness (A9: a bold takeaway plus at most one clause; flag captions over ~3 lines), and verify legibility by inspecting the rendered image (a checklist-green figure can still be an illegible mess)
8. **NOTE**: Data figures (CDFs, scatter plots, bar charts, heatmaps) should go through `/viz`, not through figure synthesis

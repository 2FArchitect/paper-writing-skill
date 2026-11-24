**Cut file**: Name a file for text cut from the article and record it in `project_context.md`.

**Craft reference**: If the student has run a literature survey (using the [literature-survey-skill](https://github.com/SNL-UCSB/literature-survey-skill) or manually), check for Pass 3+ paper notes with writing craft extractions — introduction anatomy, evaluation architecture, design section structure, and figure design choices from the strongest papers in their area. Load these as reference material for the architecture. The section structure of the best paper at your target venue is a better starting point for your outline than a generic template. Reading and writing develop together: craft patterns extracted during deep reading feed directly into the architecture of your own paper.

**Figure/table plan from visualization artifacts**: If the student has been working with the [data-visualization-skill](https://github.com/SNL-UCSB/data-visualization-skill), check for `plot_context.md` files and WALTER narrations. Each `plot_context.md` records the intent, variable mappings, plot type rationale, and design decisions for a figure — these are ready-made entries for the figure/table plan below. Each WALTER narration (Hypothesis → Axes → Look here → Trend → Exception → Result) maps directly to the evaluation prose that will accompany the figure. The iteration the student did in the viz skill — exploring what the data shows, forming predictions, confronting surprises — has already determined which figures carry the argument. The architecture should reflect that.

Output a structured table:

| Section | Pages | Key claim | Figures/Tables |
|---------|-------|-----------|----------------|
| ... | ... | ... | ... |

**Non-data figure specs**: For each figure in the plan that is NOT a data figure (architecture diagrams, pipeline illustrations, concept diagrams, comparison schematics), read `figure_synthesis_guide.md` and run spec mode to produce a `figure_spec.md`. Data figures (CDFs, bar charts, heatmaps, scatter plots) should be routed to the [data-visualization-skill](https://github.com/SNL-UCSB/data-visualization-skill). The boundary is clear: if the figure requires experimental data to render, it goes through `/viz`; if it illustrates structure, flow, or concepts, it goes through figure synthesis.

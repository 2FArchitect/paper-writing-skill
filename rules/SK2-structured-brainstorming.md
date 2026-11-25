## Structured Brainstorming — The Skill's Centerpiece

**The biggest obstacle for students isn't writing — it's that their ideas live as unstructured intuitions.** They know something is interesting but can't articulate what or why. The brainstorming process transforms scattered thinking into a precise project context that drives every section of the paper.

### How It Works

Walk the author through the 6 phases interactively. The phases are:

| Phase | Focus | Key outcome |
|-------|-------|-------------|
| 1. Problem Discovery | Who suffers, what breaks, why it breaks structurally | The opening paragraph's stakes and the Problem Gap |
| 2. Contribution Crystallization | Core claim, headline number, key abstraction name | The identity sentence and contribution list |
| 3. Evaluation Design | Baselines, metrics, datasets, experiment-to-claim mapping | The evaluation plan that constrains what the introduction can promise |
| 4. Positioning and Framing | Venue fit, competitive positioning, category creation vs. competition | The Related Work positioning sentence |
| 5. Architecture and Constraints | Design pipeline, locked decisions, open questions | The Design section's structure and the project's scope |
| 6. Narrative Spine | Story arc, the "inevitable" moment, the tweet-length pitch | The thread connecting every section |

### Rules for Running Brainstorming

- **Go phase by phase.** Don't skip ahead. Phase 1 (the problem) must be clear before Phase 2 (the contribution) makes sense.
- **"I don't know" is a valid answer.** Flag it as an open question and move on. Gaps discovered now are cheap to fix; gaps discovered during review are expensive.
- **Push back on vague answers.** "It's faster" → "Faster for whom? By how much? On what workload?" Every answer should be specific enough to appear in the paper.
- **Distinguish structural from quantitative.** "Existing tools aren't accurate enough" is quantitative — it motivates more experiments. "Existing tools assume stationarity, which fails on non-stationary workloads" is structural — it motivates a new approach. Papers need structural gaps.
- **After all phases, generate `project_context.md`** using the template in `examples/project_context.md`. See `examples/example_project_context.md` for a synthetic example of what a complete project context looks like.

## Mode 1: Spec — "What does this figure need to show?"

### Step 1: Identify Non-Data Figures

Read `project_context.md` → "Key Figures Needed" section. For each figure listed:

1. **Classify as data or non-data.** Ask: "Does this figure require experimental data to render?"
   - Yes → route to `/viz`. Tell the student.
   - No → continue here.
2. **Assign an archetype** from the table above. If ambiguous, ask the student.
3. **Confirm the generation backend** (AI image or TikZ). State the default and let the student override.

Present a summary table:

| # | Figure | Section | Archetype | Backend |
|---|--------|---------|-----------|---------|
| 1 | ... | ... | ... | ... |

### Step 2: Walk Through Archetype-Specific Questions

For each non-data figure, ask the questions below. Skip questions the student has already answered in `project_context.md`. Push back on vague answers — every answer should be specific enough to appear in a generation prompt.

#### Architecture Overview Questions

1. What is the system's name?
2. How many major stages/phases does it have? Name them.
3. What is the input to the first stage? What is the output of the last stage?
4. For each stage: what transformation does it perform? What goes in, what comes out?
5. Which stage is the paper's key contribution? (This gets visual emphasis.)
6. Are there any parallel paths or branches in the pipeline?
7. Are there feedback loops or iterative components?
8. What groupings make sense? (e.g., "Offline training" vs. "Online inference")
9. Does the figure need to show data shapes/dimensions at each stage?

#### Pipeline / Process Flow Questions

1. What is being transformed? (e.g., "raw logs → structured events")
2. How many transformation steps are there?
3. For each step: what is the operation? Is it standard (off-the-shelf) or novel?
4. Where does the pipeline branch or merge?
5. Should intermediate data representations be shown (e.g., tensor shapes, data examples)?
6. Does the pipeline have a natural direction (left-to-right for temporal, top-to-bottom for processing depth)?

#### Component Detail Questions

1. Which component from the architecture overview is being expanded?
2. What are the sub-components inside it?
3. What are the internal data flows between sub-components?
4. Are there configurable parameters that should be annotated?
5. What makes this component different from a standard implementation?

#### Concept Illustration Questions

1. What is the concept you need to illustrate?
2. What is the reader's likely misconception or default mental model?
3. What type of illustration best corrects that misconception?
   - **Before/after**: "Here's the problem state → here's the improved state"
   - **Spatial analogy**: "Think of this as a 2D space where..."
   - **Visual metaphor**: "This works like a funnel / bridge / filter..."
   - **Process contrast**: "Existing approach does X; ours does Y"
4. What are the concrete elements in the illustration? (No abstract blobs — every shape must represent something named.)
5. Where is the "aha moment" — the point where the reader sees why the old way fails?

#### Comparison Schematic Questions

1. What two approaches are being compared?
2. What is the shared input to both approaches?
3. Where exactly does the existing approach fail? (Name the specific step or assumption.)
4. Where exactly does the proposed approach succeed? (Name the corresponding step.)
5. What structural element is different between the two? (Not just "ours is better" — what specific mechanism differs?)
6. Are there components shared between both approaches? (These should be visually identical.)

#### Taxonomy / Classification Questions

1. What is being classified? (Papers? Techniques? Systems?)
2. What are the axes or dimensions of classification?
3. Which quadrant/category/branch does this paper occupy?
4. Is the key insight that this paper fills an **empty quadrant** or creates a **new branch**?
5. What specific prior works go in each category? (Name them — "Work A [citation]".)
6. Is this a 2x2 matrix, a hierarchical tree, or a Venn diagram?

#### Deployment / System Diagram Questions

1. What is the deployment environment? (Cloud, edge, campus network, ISP backbone, etc.)
2. What are the infrastructure layers? (Client → Edge → Core → Cloud)
3. What components exist at each layer?
4. What are the network connections? Distinguish data plane from control plane.
5. Are there replication factors, scale indicators, or trust boundaries to show?
6. Where does the paper's system sit in this deployment? (Which component is "ours"?)

### Step 3: Generate the Figure Spec

Read `figure_templates/figure_spec_template.md`. Fill in every field from the student's answers:

1. **Identity section**: figure ID, section, placement, archetype, backend.
2. **Purpose section**: copy the claim from `project_context.md` verbatim. Write the "what it shows" and "why it exists" from the student's answers.
3. **Content section**: build the Components, Connections, and Groupings tables from the archetype-specific answers.
4. **Layout section**: flow direction, hierarchy levels, symmetry constraints, size target (from `figure_templates/venue_styles.md`).
5. **Styling section**: assign colors from the Paul Tol palette based on semantic roles. Note which component gets emphasis.
6. **For AI backend**: assemble the generation prompt using the template from `figure_templates/prompt_templates.md`. Fill all placeholders. Append the styling block from `venue_styles.md`.
7. **For TikZ backend**: note which skeleton from `figure_templates/tikz_skeletons.md` to start from.
8. **Caption**: draft an interpretive caption following craft_reference.md rules — claim-first, states the takeaway.

Save the completed spec as `figure_spec_[fig_id].md` in the paper's `figures/` directory (create the directory if needed).

Tell the student: "Figure spec saved to `figures/figure_spec_[fig_id].md`. Run `/paper-writing figure generate` to produce the figure."

## Mode 2: Generate — "Produce the figure"

### Step 1: Read the Figure Spec

Load `figures/figure_spec_[fig_id].md`. Verify all required fields are populated. If any are missing, return to spec mode for that field.

### Step 2: Route by Backend

#### AI Image Generation Path

1. Read the assembled prompt from the spec's "Generation prompt" field.
2. **If the student has a Gemini API key** (check environment variable `GEMINI_API_KEY` or ask):
   - Generate the image by running a Python script that calls the Gemini API.
   - Save the result to `figures/fig_[short_id].png`.
   - Display the image for the student to review.
3. **If no API key is available:**
   - Present the assembled prompt to the student.
   - Instruct them to paste it into their preferred image generation tool (Gemini, DALL-E, Midjourney, etc.).
   - After they provide the generated image, proceed to critique mode.

**Iteration**: If the first result is unsatisfactory, refine the prompt:
- Be more specific about spatial layout ("component A is directly above component B, connected by a downward arrow")
- Add negative instructions ("do NOT show component X as a circle, use a rectangle")
- Adjust emphasis ("make the contribution component 1.5x larger than the others")
- Cap at 3 prompt iterations before suggesting manual refinement in a drawing tool.

#### TikZ Path

1. Read the archetype from the spec. Load the corresponding skeleton from `figure_templates/tikz_skeletons.md`.
2. Customize the skeleton:
   - Replace placeholder nodes with the actual components from the spec.
   - Set colors from the spec's color mapping.
   - Adjust layout (node distances, positioning) to fit the actual component count.
   - Add all connections, groupings, and annotations from the spec.
   - Set the figure width to match the venue target from `figure_templates/venue_styles.md`.
3. Write the TikZ code to `figures/fig_[short_id].tex`.
4. **Compile** (if `pdflatex` is available):
   ```bash
   cd figures && pdflatex -interaction=nonstopmode fig_[short_id].tex
   ```
   - If compilation fails, read the error log, fix the TikZ code, and retry (max 3 attempts).
   - If compilation succeeds, display the PDF for the student to review.
5. **If `pdflatex` is not available:**
   - Present the TikZ code to the student.
   - Instruct them to compile in Overleaf or their local TeX installation.

### Step 3: Update the Spec

After generation, update the `figure_spec.md`:
- Set "Generated: yes" with today's date
- For TikZ: record the source file path
- For AI: save the successful prompt version and the output image path

Tell the student: "Figure generated. Run `/paper-writing figure critique` to review it against your paper's claims and venue standards."

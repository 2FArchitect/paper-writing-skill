## Evaluation (6-Move Sequence)

| Move | Function | What it looks like |
|------|----------|-------------------|
| 1. Setup Anchoring | Dataset, baselines, metrics | Compressed. Just enough for reproducibility, not a technical report. |
| 2. Head-to-Head | Direct comparison vs. named baselines | The paper's core evidence. Baselines NAMED, not "prior work." |
| 3. Deep Dive | Disaggregated analysis | Break down by meaningful conditions. Show WHERE the system helps most and least. |
| 4. Takeaway Synthesis | Pattern statement after each experiment cluster | Ties results to claims. Prevents readers from drawing wrong conclusions. |
| 5. Ablation | Design choice validation | Shows each component contributes. Answers "is your design over-engineered?" |
| 6. Robustness | External validity | Temporal generalization, spatial generalization, computational overhead. |

**Evolution**: Student drafts use Move 2 only (head-to-head). The advisor adds Moves 3–6. The Takeaway (Move 4) is the signature addition — absent from all early drafts, present in all final versions.

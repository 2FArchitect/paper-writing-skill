## Design (5-Move Sequence)

| Move | Function | What it looks like |
|------|----------|-------------------|
| 1. Abstraction Introduction | User-facing mental model | Present what users reason about, not what the system computes internally. |
| 2. Design Justification | Why THIS design | Often a negative result: "the obvious approach fails because X." Makes the chosen design feel inevitable. |
| 3. Component Architecture | Named stages/modules | Always a pipeline or structured flow the reader can trace. Component names become the evaluation's vocabulary. |
| 4. Key Design Decision | The non-obvious "knob" | A configurable parameter that shows the system isn't one-size-fits-all. |
| 5. Robustness | What happens when assumptions fail | Often added late per reviewer/advisor feedback. Signals defensive design awareness. |

**Anti-patterns**: Opening with implementation details (not abstractions). Formal math replacing intuition. Missing the "why" argument.

## Principle 9: Dual Evaluation for Dual Contributions

If a paper makes two fundamentally different types of claims (e.g., "the system works correctly" AND "the system improves downstream performance"), the evaluation must be split into separate sections. A monolithic evaluation that mixes claim types produces confusion because each claim requires different baselines, metrics, and experimental design.

**The test**: Can each evaluation subsection be described with a single sentence of the form "This section shows that [specific claim]"? If a subsection argues for multiple claims, it needs to be split.

**Rule**: Before writing the evaluation, list every claim from the introduction. Map each claim to baselines, metrics, and experiments. If two claims require different experimental designs, they belong in separate subsections.

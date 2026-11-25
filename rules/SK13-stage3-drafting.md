**Per-section scaffolding**: Before writing any section's full prose, write the topic sentences first. Read them in sequence — they should form a coherent argument on their own. If the topic sentences don't flow, the paragraphs won't either. Fill in the full paragraphs only after the topic-sentence sequence holds together. In LaTeX, a practical technique is to annotate each paragraph with a purpose comment before writing prose:

```latex
\section{Introduction}
% Stakes: who suffers and why the domain matters.
...
% Problem gap: structural limitation of current approaches.
...
% Key abstraction: named concept that captures our insight.
...
% Contributions: numbered, claim-first list.
...
```

Each comment is a contract: the paragraph that follows must deliver on it. If a paragraph doesn't fit any comment, either the paragraph doesn't belong or a comment is missing.

**Numbers from data**: every number computed from the paper's own data enters the text through a macro written by the analysis script that computes it (for example, the script writes `generated/<script>.tex` with one `\defval{name}{value}` per value, and the text writes `\val{name}`). Never type such a number by hand; the script does the rounding and formatting. Numbers quoted from sources stay literal, with their citations. When a script run changes a value, re-read every sentence that uses it before committing: the number updates itself, the words around it do not.

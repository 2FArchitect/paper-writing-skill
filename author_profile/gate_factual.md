## Group 4 — Rigor and grounding

**S15. Mappability: no orphan numbers (CRITICAL).** Every number, table cell, and empirical claim
maps to a committed analysis script → a committed raw result file → (for reproduced prior-work
metrics) the source it reproduces. Maintain a provenance note (claim → value → script → raw
output). Numbers from the paper's own data reach the text only through script-generated macros 
(SKILL.md, Stage 3); a data number typed into the prose is a finding. New analysis code is 
committed to the correct repository, not a scratch dir. If a number cannot be mapped, cut it or 
generate the mapping.

**S16. Ground critiques in numbers, not assertions (MAJOR).** "Prior work X is not enough" is weak
as an assertion. Make it a head-to-head: run the prior method's OWN metric on the cases it omitted
and show what it does and does not reveal, beside your reading. A reproducible contrast beats a
rhetorical one and is honest.

**S17. Data-integrity guard (CRITICAL).** Before citing a computed number, verify the input is not
a broken/degenerate extraction or an uncontrolled artifact (unique-row counts, variance, provenance
caveats). Never cite a number flagged as not-yet-validated.

**S18. Hedge scan (MAJOR).** Paper-wide: flag every empirical or causal universal ("X takes / means
/ is Y") and ask "always, or typically/often?" Add the calibrated hedge where the claim outruns the
evidence. (This is the one place hedging is ADDED — everywhere else the base rule is zero hedging;
see `craft_reference.md` on calibrated confidence.)

**S32. Citation authenticity and bibliographic accuracy (CRITICAL).** Numbered out of sequence to
avoid renumbering S19–S31 elsewhere in this file and in cross-references (`README.md`, `CLAUDE.md`,
`loop_mode.md`) — it belongs here, thematically, alongside S15–S18's grounding checks. Every `.bib`
entry names a real, verifiable source, never a plausible-sounding fabrication. For each entry
check: (a) the paper/RFC/standard exists — a copy is saved locally, and (b)–(d) are checked against
that copy, never from model memory alone; (b) the author list is complete, in the paper's
actual byline order (not alphabetized, not truncated with "and others"/"et al." in the `.bib`
itself); (c) the title matches the published title exactly, not a paraphrase; (d) the venue and
year are correct — watch for a paper that exists under a *different* title/venue/year than the one
cited, and for a citation key's year silently disagreeing with its own year field (a tell that two
real publications got conflated). Run this on every new `.bib` entry before it ships, and as a
full-bibliography audit before submission — LLM-generated citations hallucinate, misattribute
authors, or conflate two real papers often enough that "it sounds right" is not evidence.

Grep aid (catches truncation outright; everything else needs a real lookup, not a pattern match):
```bash
grep -n "and others\|et al\." *.bib
# Flag any key whose year prefix disagrees with its own year field, e.g. key `foo2011x` with `year = {2012}`:
grep -oE '@[a-z]+\{[a-z]+([0-9]{4})[a-z]*,' *.bib | grep -oE '[a-z]+([0-9]{4})[a-z]*,' # inspect each against its entry's year field
```

First applied 2026-07-30 against a 32-entry chapter bibliography: 28 entries confirmed clean via
Crossref/RFC-Editor/dblp lookups, 4 real discrepancies found and fixed — a one-year-off publication
date, two real papers' metadata conflated under one entry, an RFC cited under the wrong number
entirely (title matched a *different* RFC than the cited number), and an 11-author truncation
("and others") on a 21-author paper. Zero outright hallucinations, but every one of the four would
have misled a reader trying to find the actual source.

## Group 5 — Structure and framing

**S21. Honest, building-upon positioning — especially of your OWN prior work (CRITICAL).**
Acknowledge what prior work attempted; do not claim it "ignored" something it treated superficially
— state the real delta. Frame your contribution as building upon / operationalizing it, not
trashing it; avoid "cannot / useless / backward" as blanket verdicts. Any critique is scoped and
evidence-backed (S16). No inconsistency between how Related Work, Background, and Intro describe the
same prior work.

## Principle 14: Technical Claims Require Citations

Every technical claim in a paper must be grounded with a citation or an explicit cross-reference. When section N references content that was established with citations in section M, it must either carry forward the relevant `\cite{}` commands or use an explicit forward/backward reference (`\S\ref{}`). Uncited technical claims — no matter how well-established — read as unsupported assertions to reviewers.

**Common violation**: A design section restates failure modes or properties described in the background section but drops all the citations that supported those claims. The result looks like the authors are asserting without evidence.

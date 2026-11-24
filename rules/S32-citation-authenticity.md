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

**1. Page count.** Extract page count from the compiled PDF and compare against the venue's limit (from `project_context.md`). Flag whether references/appendices count — this varies by venue.
```bash
pdfinfo paper.pdf | grep Pages
```

**2. Broken references.** Search `.tex` source files for unresolved references that will render as `[?]` or `??` in the PDF. Also check the `.log` file for LaTeX warnings about undefined references and citations.
```bash
grep -n "LaTeX Warning.*undefined" paper.log
grep -rn '\\cite{' *.tex | grep -v '%' # list all citations for cross-check
```

**3. Embedded fonts.** Verify all fonts are embedded. Non-embedded fonts cause rendering differences across machines and are rejected by some submission systems.
```bash
pdffonts paper.pdf | grep -v "yes"
```
If any font shows `no` in the `emb` column, flag it and suggest adding `\usepackage[T1]{fontenc}` or compiling with `GS_OPTIONS=-dPDFSETTINGS=/prepress`.

**4. Figure quality.** Check that all included figure files are vector format (PDF/EPS) or high-resolution raster. List all figures referenced in the source and verify they exist.
```bash
grep -rn '\\includegraphics' *.tex  # list all figure references
file figures/*.pdf figures/*.png 2>/dev/null  # check file types
```
Flag any PNG/JPG figures — these should be vector unless they are photographs or screenshots.

**5. Anonymization (if double-blind).** Search all `.tex` files for author names, institution names, grant numbers, acknowledgment sections, and self-citations that could reveal identity.
```bash
grep -rni 'AUTHOR_NAMES_HERE\|INSTITUTION_HERE\|\\thanks\|acknowledgment' *.tex
```
Replace `AUTHOR_NAMES_HERE` and `INSTITUTION_HERE` with actual names from `project_context.md` before running.

**6. Column balancing.** Check whether the `balance` package is loaded (for two-column formats). If not, suggest adding `\usepackage{balance}` and `\balance` before `\bibliography`.
```bash
grep -rn 'balance' *.tex
```

**7. Common LaTeX issues.** Scan for frequently missed mechanical problems:
```bash
grep -rn '\\cite{.*}' *.tex | grep -v '~\\cite'  # missing ~ before \cite (dangling references)
grep -rn 'et al\.' *.tex | grep -v '~'  # missing ~ after "et al."
grep -rn '\\label{' *.tex | sort | uniq -d  # duplicate labels
```

**Report format**: Run all checks, then present a single summary table:

| Check | Status | Details |
|-------|--------|---------|
| Page count | ✓ or ✗ | N pages (limit: M) |
| Broken refs | ✓ or ✗ | List of undefined refs |
| Embedded fonts | ✓ or ✗ | List of non-embedded fonts |
| Figure quality | ✓ or ✗ | List of raster figures |
| Anonymization | ✓ or ✗ | List of leaks found |
| Column balance | ✓ or ✗ | Package present/missing |
| LaTeX issues | ✓ or ✗ | Count of dangling refs, duplicate labels |

Fix what can be fixed automatically (e.g., adding `~` before `\cite`). Flag what requires the author's decision (e.g., replacing a raster figure with vector).

# Artifact Gate — compile, render, and inspect the PDF

> The gates in `gate_mechanical.md` and `gate_semantic.md` audit the **source**. A paper is
> source **plus a rendered artifact**, and figures, tables, and page layout ship in the artifact,
> not the source. This gate catches what a text-only pass cannot see: a float that overflows the
> column, a table that dies in grayscale, a caption that runs six lines, a `figure*` reused from
> another template that now bleeds off the page. **Run it on every edit that touches a float,
> caption, or table, and once before every "done."** A source-only audit is half a gate; do not
> report a section "audited" until you have compiled it and *looked* at the page.

This gate has two parts: **Part A** is mechanical (grep the `.log`, deterministic). **Part B** is
judgment (render each changed page to an image and inspect it). Both must run. Report the Part A
counts and paste or describe the Part B rendered evidence; a mental pass is not a run.

---

## Part A — Log gate (grep the compile log, fix every hit)

Compile the paper with its own build, then grep its compile log. Each rule states the ban and the fix.

@../rules/A1-compile-succeeds.md

@../rules/A2-overfull-boxes.md

@../rules/A3-undefined-references.md

@../rules/A4-missing-assets.md

---

## Part B — Render gate (look at the page)

Render every changed page to an image and inspect it. These
are the checks a regex cannot make.

@../rules/A5-no-clipped-floats.md

@../rules/A6-refit-reused-floats.md

@../rules/A7-legible-with-units.md

@../rules/A8-no-color-only.md

@../rules/A9-caption-and-placement.md

---

## Process

1. Compile with the paper's own build.
2. Part A: run the four log greps; fix or justify every hit. Report the counts.
3. Part B: render every changed page; inspect each float against A5–A9. Report what you saw, with
   the rendered image as evidence, not "looks fine."
4. Only source that passes `gate_mechanical` **and** `gate_semantic` **and** this gate is reported
   done. If the independent red-team (`red_team_protocol.md`) runs, hand it the **rendered page
   images**, not only the `.tex`, so it can catch layout and float defects a source read cannot.

**Data figures** (CDFs, bar charts, heatmaps, scatter plots) are authored in the
[data-visualization skill](https://github.com/SNL-UCSB/data-visualization-skill); this gate enforces
that whatever ships in the PDF still passes A5–A9 in the final template. Route a failing data figure
back to `/viz` rather than hand-patching it here.

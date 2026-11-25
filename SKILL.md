---
name: paper-writing
description: "Research paper writing assistant that enforces the SNL lab's editorial principles and voice profile (customizable) and a staged writing workflow. MANDATORY TRIGGERS: Use this skill whenever the user mentions writing a paper, drafting a section, revising a section, editing a paper, reviewing a draft, rewriting an introduction, writing an evaluation, polishing prose, compressing text, or any task involving .tex files, Overleaf, conference submissions, or paper deadlines. Also trigger when the user names their paper in a writing context. This skill should activate for ANY research writing task — sections, abstracts, rebuttals, camera-ready edits, cover letters, or response to reviewers."
arguments: [mode, step]
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/mode_files.sh *)
hooks:
  PreToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: test -f "__PAPER_GUARD__" && python3 "__PAPER_GUARD__" mark || true
          once: true
        - type: command
          command: test -f "__BASH_GUARD_INSTALL__" && python3 "__BASH_GUARD_INSTALL__" --quiet || true
          once: true
---

# Paper Writing Skill

## How This Skill Works

This skill encodes the writing methodology of the [Systems and Networking Lab (SNL)](https://github.com/SNL-UCSB) at UC Santa Barbara, derived from forensic analysis of 6 papers (8 submissions), 7,600+ Overleaf edits, 100+ tex file versions, and 5 peer review processes. See [*The Paper Behind the Paper*](https://sites.cs.ucsb.edu/~arpitgupta/blog/the-paper-behind-the-paper.html) for the full analysis. It works out of the box — the default rules are calibrated and battle-tested.

### Three Layers

1. **The pipeline (fixed)**: A five-stage writing workflow. Does not change between users or papers.

2. **The voice and editorial rules (defaults provided, customizable)**: Sentence-level style, structural rules, compression patterns, section checklists. These ship with the SNL lab's rules as defaults. Students may customize by editing files in `author_profile/` — see the README for what to change.

3. **The project context (per paper)**: Identity sentence, venue, contribution claims, locked decisions. Lives in a `project_context.md` in the paper's working directory.

### How This Skill Connects to the Research Pipeline

This skill does not operate in isolation. It is part of a three-skill family, and the artifacts from the other two skills are direct inputs to the writing process:

**From the [literature-survey-skill](https://github.com/SNL-UCSB/literature-survey-skill):**
- **Gap analysis** → feeds Brainstorming Phase 1 (Problem Discovery). The gaps the survey identified — missing quadrants, shared assumptions that break, unexplored combinations — are the structural limitations that motivate your paper.
- **Writing craft extractions** (Pass 3+) → feed the Architecture stage and section drafting. The introduction anatomy, evaluation architecture, and design craft you extracted from the best papers in your area are the models for your own paper's structure.
- **Competitive positioning** → feeds Brainstorming Phase 4. The invariant matrix and dependency graph from synthesis show exactly where your paper sits relative to existing work.

**From the [data-visualization-skill](https://github.com/SNL-UCSB/data-visualization-skill):**
- **Exploration** (`exploration_log.md`) → feeds Brainstorming Phase 3 (Evaluation Design). The exploration forced you to look at your data from multiple angles before forming hypotheses. The surprises you found — distributions you didn't expect, subgroups that behaved differently — shape what claims are defensible and where the real contribution lives.
- **Brainstorm** (`braindump.md`) → feeds the figure/table plan. Each braindump articulates what question a figure answers, what you expected to see, and what would surprise you. These are the hypotheses your evaluation must validate.
- **Plan + Execute** (`plot_context.md`) → feeds the Architecture stage's figure/table plan. Each plot_context records intent, variable mappings, plot type rationale, and design decisions — ready-made entries for the paper's figure plan.
- **Analyze** (WALTER narrations) → feeds Evaluation Move 4 (Takeaway Synthesis). The WALTER Result — "what is the takeaway? does it connect back to the hypothesis?" — is a first draft of the Takeaway paragraph for that experiment cluster.

The three skills create a closed loop: the literature survey reveals the gap and teaches you how accepted papers communicate; data visualization forces you to understand what your evidence actually shows and what hypotheses it validates; paper writing turns both into a publishable argument. **If the student has artifacts from the other skills, Claude MUST load them.**

### When This Skill Triggers, Claude MUST:

1. Read this SKILL.md (already loaded)
2. Read the files for the mode (see **Modes** below) — they hold the editorial rules for this step
3. Ask which paper the user is working on
4. Look for a `project_context.md` in the paper's working directory
5. If found, read it and treat it as binding constraints
6. If not found, decide how to create one: if the ideas already exist in notes, drafts, code and related work, run `/paper-writing story`; if they are mostly in the user's head, run `/paper-writing brainstorm`
7. Check for artifacts from sibling skills — survey paper notes with craft extractions, `exploration_log.md`, `braindump.md`, `plot_context.md`, WALTER narrations. If found, load them as reference material for the relevant pipeline stages
8. Check for a **private overlay skill**: an installed skill whose name ends in `paper-writing-lab` (for example `~/.claude/skills/paper-writing-lab/` or `~/.claude/skills/<group>-paper-writing-lab/`). If present, read it: it carries a group's real worked cases, house rules and project records that cannot live in this public skill. Its project-specific guidance takes precedence over the defaults here; never copy its contents into this repository

---

## Modes

Run as `/paper-writing <mode> [step]`. If the user gave no mode ask them, or select it yourself if it's obvious from their request or from the project status, then invoke this skill again with that mode (and step). For `draft` and `rewrite`, the step is the section's name as the paper uses it, for example `/paper-writing draft results`. `draft intro` is Draft 0, written before the evaluation exists; `rewrite intro` is the final introduction, written after the evaluation is complete.

!`${CLAUDE_SKILL_DIR}/scripts/mode_files.sh "${CLAUDE_PROJECT_DIR}" $mode $step`

If a mode file's text is no longer in context (for example after compaction), read it again.

| Mode | What it is for |
|---|---|
| `story` | The paper's ideas are spread across notes, drafts, code and related work: turn them into a story and outline (Stage 1) |
| `brainstorm` | The ideas are mostly in the author's head, or a new paper is starting: build `project_context.md` (Stage 1) |
| `architecture` | Section outline, claims per section, figure/table plan, page budget (Stage 2) |
| `draft <section>` | First draft of one section (Stage 3) |
| `rewrite <section>` | The section written again from a blank page, with the old version as reference: the final introduction (`rewrite intro`), or any section whose framing changed (Stage 3) |
| `integrate` | Consistency pass across all sections (Stage 4) |
| `compress` | Cut what the paper does not need (Stage 5) |
| `submit-check` | Mechanical checks before submission |
| `critique` | Feedback on a draft: numbered findings with severity, the principle each breaks, and a concrete rewrite |
| `respond` | Responses to the venue's reviewers |
| `figure spec`, `figure generate`, `figure critique` | Non-data figures (architecture diagrams, pipeline illustrations, concept diagrams). Data figures go to the data-visualization skill (`/viz`) |
| `loop` | Repeated audit-and-fix, one section per pass |

---

## The Five-Stage Pipeline

Every paper goes through these stages in order. Claude identifies which stage the user is in and enforces that stage's rules.

### Stage 1: Structured Brainstorming → Project Context Creation

**Gate**: The user must have a one-sentence identity statement and contribution claims written as results. If they don't, run the mode below. Don't rush — this is the most important stage. A vague project context produces a vague paper.

**Mode**: `/paper-writing brainstorm`, or `/paper-writing story` when the ideas already exist in notes, drafts, code and related work (step 6 above).

### Stage 2: Architecture

**Gate**: Section outline with claim assignments, per-section narrative arcs, figure/table plan, evaluation structure, and page budget.

**Mode**: `/paper-writing architecture`.

### Stage 3: Section Drafts

**Enforced order**: Draft 0 Introduction → Evaluation → Design/Method → Background → Related Work → Final Introduction → Abstract.

The introduction is written **twice**. This is the most impactful principle in the entire system (Principle 1).

**Draft 0 Introduction** comes first. It is a framing scaffold — stakes, problem gap, rough contribution claims — that sets guardrails for the evaluation. Draft 0 clarifies what the paper is *trying* to show. It is explicitly disposable: it probably will not survive to the final version. Writing is a thinking tool, not just a communication tool — Draft 0 forces the student to externalize their framing before designing experiments.

**The evaluation** comes next, constrained by Draft 0's guardrails. Then Design, Background, and Related Work.

**The final introduction** is rewritten from scratch after the evaluation is complete. It promises exactly what the evidence supports — no more, no less. Draft 0 is reference material, not a starting point for editing. If the user asks to skip Draft 0 and go straight to evaluation, explain that evaluation without framing guardrails produces experiments that don't build toward a unified argument.

**Modes**: `/paper-writing draft <section>` for each section; `/paper-writing rewrite intro` for the final introduction; `/paper-writing rewrite <section>` for any section whose framing changed.

### Stage 4: Integration

**Mode**: `/paper-writing integrate`: consistency pass across all sections.

### Stage 5: Compression

**Mode**: `/paper-writing compress`: cut what the paper does not need.

### Pre-Submission Mechanical Checklist (Automated)

**Mode**: `/paper-writing submit-check`: mechanical checks before submission.

---

## How to Respond to Common Requests

The answer to each request is in its own file in this skill's `faq/` folder. Read the file when the user's request matches.

- "Help me write section X of paper Y": `faq/write-section.md`
- "Review / critique this draft": `faq/review-draft.md`
- "Compress / tighten this section": `faq/compress-section.md`
- "I want to get feedback on this draft": `faq/get-feedback.md`
- "Help me respond to reviewers": `faq/respond-to-reviewers.md`
- "I'm starting a new paper — where do I begin?": `faq/start-new-paper.md`
- "Turn our notes into a paper outline" / "What is the story for <venue>?": `faq/notes-to-outline.md`
- "I need a non-data figure (architecture diagram, pipeline illustration, etc.)": `faq/non-data-figure.md`

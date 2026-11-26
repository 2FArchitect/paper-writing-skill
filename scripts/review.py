#!/usr/bin/env python3
"""Ask a reviewer agent questions one at a time about one section of the article.

How to run a review: the skill's review_process.md (included in SKILL.md).

Each question is one rule from the skill's rules/*.yml that has a block for this reviewer (the agent
name without its "reviewer-" prefix: reviewer-facts asks the `facts` blocks, reviewer-writing the
`writing` blocks; rules/SCHEMA.md). A rule whose `applies.sections` names section kinds is asked only
for a section of one of those kinds. The last question is always `anything`.

Greps: for the writing reviewer, each rule's text greps are run here on the text under review (the
section in the review copy), and each match, with its line number and about ten words either side, goes into that rule's question. A rule
with no matches is asked without them, or not at all when the rule has `grep_hits_only: true`.
For the facts reviewer the greps are still printed for the reviewer to run (TODO below).

The paper's own additions live in <project>/.paper-writing/:
  rules/*.yml        a file with the same `id` as a skill rule replaces it; one with no actor blocks
                     switches it off; any other id is a project rule, asked like the skill's.
  agents/<actor>.md  the project's additions to the reviewer's instructions (e.g. agents/facts.md for
                     reviewer-facts), sent as part of the opening message.

The reviewers are Claude Code agents (the skill's agents/, installed into ~/.claude/agents/ by setup).

TODO: the greps were written for LaTeX; on the Markdown review copy some
over-match (M1's `---` matches table separator rows). Modify the expressions to read Markdown.
TODO: auto-run the facts reviewer's greps too. It reads the LaTeX as well as the compiled article,
so decide which text each of its greps runs on (S32's run on the .bib files).
"""
import argparse
import glob
import random
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml  # PyYAML; setup installs it

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
from expand_includes import render_block  # noqa: E402  (one renderer for the author's and the reviewers' views)

INTERVIEW = SKILL / "scripts/agent-interview.py"
AUTO_GREP = {"writing"}  # reviewers whose greps this script runs on the text under review
HITS_INTRO = "These passages match this rule's search, which over-catches on purpose."
ANYTHING = ("Anything else: report any other problem you noticed in the section under review "
            "that no earlier question covered, in the same format.")

def load_rules(project):
    """The skill's rules, with the project's files replacing those of the same id, by id."""
    rules = {}
    for folder in (SKILL / "rules", project / ".paper-writing/rules"):
        for path in sorted(glob.glob(str(folder / "*.yml"))):
            with open(path, encoding="utf-8") as f:
                rule = yaml.safe_load(f)
            if not isinstance(rule, dict) or "id" not in rule:
                sys.exit(f"{path}: not a rule file (rules/SCHEMA.md)")
            rules[str(rule["id"])] = rule
    return rules


def applies(rule, kind):
    sections = (rule.get("applies") or {}).get("sections") or []
    return kind == "all" or not sections or kind in sections


# ---- the text under review, and the passages a rule's greps match in it

def review_text(review_copy, section):
    """(line number, line) for each line of the text under review, comment and blank lines left out."""
    lines = review_copy.read_text(encoding="utf-8").splitlines()
    if section == "all":
        start, end = 0, len(lines)
    else:
        start = next(i for i, l in enumerate(lines) if re.match(rf"^# {re.escape(section)} ", l))
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("# ")), len(lines))
    return [(n + 1, lines[n]) for n in range(start, end)
            if lines[n].strip() and not lines[n].lstrip().startswith("<!--")]


CONTEXT_WORDS = 10  # either side of a match: about one average sentence (craft_reference.md, ~21-word mean)


def snippet(line, m):
    before = line[:m.start()].split()
    after = line[m.end():].split()
    left = ("…" if len(before) > CONTEXT_WORDS else "") + " ".join(before[-CONTEXT_WORDS:])
    right = " ".join(after[:CONTEXT_WORDS]) + ("…" if len(after) > CONTEXT_WORDS else "")
    return f"{left} **{m.group(0)}** {right}".strip()


def hits(rule, text):
    """Each match of the rule's text greps in `text`, as `line: …context **match** context…`; all of
    them (a cap could leave out the ones that matter)."""
    out = []
    for g in rule.get("grep") or []:
        if g.get("target"):
            continue
        rx = re.compile(g["pattern"], re.I if "i" in (g.get("flags") or "") else 0)
        for n, line in text:
            out += [(n, m.start(), f"{n}: {snippet(line, m)}") for m in rx.finditer(line)]
    return [t for _, _, t in sorted(set(out))]


def grep_aid(rule):
    """The rule's greps as shell lines for the reviewer to run, each with the rule's action and hint."""
    out = []
    for g in rule.get("grep") or []:
        tail = " · ".join(x for x in (g.get("action"), g.get("hint")) if x)
        target = g.get("target")
        where = " (the .bib files)" if target == "bib" else f" (run on the {target})" if target else ""
        flags = "-rn" + ("i" if "i" in (g.get("flags") or "") else "") + "E"
        flags += " --include='*.bib'" if target == "bib" else ""
        pat = g["pattern"].replace("'", "'\\''")
        dashes = " --" if pat.startswith("-") else ""
        out.append(f"# {rule['id']}{where}" + (f": {tail}" if tail else ""))
        out.append(f"grep {flags}{dashes} '{pat}'")
    return out


def rule_message(rule, actor, text):
    """The question for one rule, or None when its block says to ask only on grep hits and there are none."""
    msg = f"Question {rule['id']}:\n\n{render_block(rule, actor).strip()}"
    if actor in AUTO_GREP and text is not None:
        found = hits(rule, text)
        if found:
            msg += "\n\n" + HITS_INTRO + "\n\n" + "\n".join(found)
        elif rule.get("grep_hits_only"):
            return None
        rest = [g for g in rule.get("grep") or [] if g.get("target")]
        lines = grep_aid({**rule, "grep": rest}) if rest else []
    else:
        lines = grep_aid(rule)
    if lines:
        msg += "\n\nGrep aid:\n```bash\n" + "\n".join(lines) + "\n```"
    return msg


def questions(rules, actor, kind, text):
    """The messages for this reviewer, in random order: every rule with a block for `actor` that applies
    to `kind`. `anything` is always last."""
    chosen = [r for r in rules.values() if r.get(actor) and applies(r, kind)]
    random.shuffle(chosen)
    return [m for m in (rule_message(r, actor, text) for r in chosen) if m] + [ANYTHING]


def project_instructions(actor, project):
    """The project's additions to this reviewer's instructions, for the opening message, or ""."""
    path = project / ".paper-writing/agents" / f"{actor}.md"
    if not path.is_file():
        return ""
    return "This project's instructions for you:\n\n" + path.read_text(encoding="utf-8").strip()


def section_heading(review_copy, n):
    for line in review_copy.read_text(encoding="utf-8").splitlines():
        if re.match(rf"^# {re.escape(n)} ", line):
            return line[2:].strip()
    sys.exit(f"no section '# {n} …' in {review_copy}; rebuild the paper first")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--agent", required=True, help="reviewer-facts or reviewer-writing (installed in ~/.claude/agents/ by setup)")
    ap.add_argument("--project", default=".", help="the paper's folder (default: the current folder)")
    ap.add_argument("--section", help="section number, e.g. 4; or 'all' for the whole article (closure pass)")
    ap.add_argument("--kind", help="the section's kind, as rules name it in `applies.sections` (e.g. intro, "
                                   "evaluation, related-work); required with a section number")
    ap.add_argument("--resume", metavar="SESSION_ID", help="continue a review with --ask")
    ap.add_argument("--ask", action="append", metavar="TEXT",
                    help="what you say to the reviewer (repeatable). With --resume: a follow-up "
                         "message. On a new review: added to the opening message, for instructions "
                         "specific to this review (what a draft leaves out, which figure changed), "
                         "never earlier findings, decisions or other author notes")
    ap.add_argument("--review-copy", default="build/markdown/main.md",
                    help="the compiled article, relative to --project (default: %(default)s)")
    ap.add_argument("--report", help="report file (default: a new file in notes/review-reports/)")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--dry-run", action="store_true", help="print the messages; send nothing")
    a = ap.parse_args()

    project = Path(a.project).resolve()
    actor = a.agent.removeprefix("reviewer-")
    reports = project / "notes/review-reports"

    if a.resume:
        if not (a.ask and a.report):
            ap.error("--resume needs --ask and the original --report")
        opening, msgs = None, a.ask
    else:
        if not a.section:
            ap.error("give --section (or --resume)")
        review_copy = project / a.review_copy
        if a.section == "all":
            kind = "all"
            opening = ("The whole article is under review: every section is the section under "
                       "review, and findings may be about any part of it.")
        else:
            if not a.kind:
                ap.error("give --kind with --section (the section's kind, as rules name it in applies.sections)")
            heading = section_heading(review_copy, a.section)
            kind = a.kind
            opening = f"The section under review is {heading} (\"# {heading}\" in the review copy)."
        extra = project_instructions(actor, project)
        if extra:
            opening += "\n\n" + extra
        if a.ask:
            opening += "\n\n" + "\n\n".join(t.strip() for t in a.ask)
        rules = load_rules(project)
        named = sorted({k for r in rules.values() for k in (r.get("applies") or {}).get("sections") or []})
        if kind != "all" and kind not in named:
            print(f"note: no rule names the kind '{kind}', so only the rules for every section are asked. "
                  f"Kinds the rules name: {', '.join(named)}.", file=sys.stderr)
        text = review_text(review_copy, a.section) if actor in AUTO_GREP else None
        msgs = questions(rules, actor, kind, text)

    if a.dry_run:
        if opening:
            print(f"=== Opening\n{opening}\n")
        for i, m in enumerate(msgs, 1):
            print(f"=== Message {i} of {len(msgs)}\n{m}\n")
        return

    reports.mkdir(parents=True, exist_ok=True)
    report = Path(a.report).resolve() if a.report else \
        reports / f"{'whole' if a.section == 'all' else 's' + a.section}-{a.agent}-{time.strftime('%Y-%m-%d-%H%M')}.md"
    with tempfile.TemporaryDirectory() as tmp:  # the messages, for the interview script; the report quotes them all
        run = Path(tmp)
        (run / "questions.md").write_text("\n---\n".join(msgs) + "\n", encoding="utf-8")
        cmd = [sys.executable, str(INTERVIEW), "--agent", a.agent,
               "--cwd", str(project), "--questions", str(run / "questions.md"), "--report", str(report),
               "--model", a.model, "--effort", a.effort]
        if opening:
            (run / "opening.md").write_text(opening + "\n", encoding="utf-8")
            cmd += ["--opening", str(run / "opening.md")]
        else:
            cmd += ["--resume", a.resume]
        code = subprocess.call(cmd)
    sys.exit(code)


if __name__ == "__main__":
    main()

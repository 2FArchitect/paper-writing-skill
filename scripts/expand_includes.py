#!/usr/bin/env python3
"""Expand @path include lines in a Markdown file and print the result.

Usage: expand_includes.py FILE

An include is a line that holds nothing but @path (leading/trailing whitespace allowed). The
line is replaced by the full text of the file it names. The rules follow Claude Code's CLAUDE.md
imports (https://code.claude.com/docs/en/memory.md, "Import additional files"):

  - a relative path resolves relative to the file containing the include, not the working
    directory;
  - included files are expanded too (nested includes);
  - lines inside fenced code blocks are never includes;
  - a space in a path is written as a backslash before the space.

One difference: an @path in the middle of other text is left alone; only a whole line counts.
An include that names a missing file, or that includes itself through a cycle, is an error.

Rule files (rules/*.yml, format in rules/SCHEMA.md) render one actor's view:

  @../rules/M5-banned-adjectives.yml            the author's block
  @../rules/M5-banned-adjectives.yml#writing    that actor's block
  @../rules/M5-banned-adjectives.yml#reviewers  every actor except the author, in file order

A rule with no block for the requested actor renders nothing. The line

  @@grep-script

renders a bash block holding every text grep (entries without a `target`) of every rule file in
rules/, one group per rule, with the rule's action and hint as a comment.
"""
import glob
import os
import re
import sys

INCLUDE = re.compile(r"^\s*@((?:\\ |\S)+)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
META = {"id", "title", "kind", "severity", "applies", "merged", "source", "exceptions", "grep", "notes"}


def load_rule(path):
    import yaml  # PyYAML; setup installs it
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def actors_of(rule):
    return [k for k in rule if k not in META]


def render_block(rule, actor):
    """One actor's view of a rule, as Markdown. Order: text, questions, why, exceptions, examples."""
    block = rule.get(actor)
    if not block:
        return ""
    out = []
    kind = rule.get("kind")
    if kind == "principle":
        n = re.sub(r"\D", "", rule["id"])
        out.append(f"## Principle {n}: {rule['title']}\n")
    elif kind == "checklist":
        out.append(f"## {rule['title']}\n")
    text = (block.get("text") or "").rstrip()
    if text:
        out.append(text + "\n")
    for question in block.get("questions") or []:
        out.append(f"- [ ] {question}\n")
    why = (block.get("why") or "").rstrip()
    if why:
        out.append("\n" + why + "\n")
    exceptions = rule.get("exceptions") or []
    if exceptions:
        out.append("\n")
        for e in exceptions:
            e = e.rstrip()
            out.append(("- Exception: " + e + "\n") if "\n" not in e else ("- Exception: " + e.replace("\n", "\n  ") + "\n"))
    ex = block.get("examples") or {}
    good, bad = list(ex.get("good") or []), list(ex.get("bad") or [])
    if good or bad:
        out.append("\n")
        if good and bad and len(good) == len(bad):
            for b, g in zip(bad, good):
                out.append(f"- ✗ `{b}` → ✓ `{g}`\n")
        else:
            if bad:
                out.append("- ✗ " + " · ".join(f"`{b}`" for b in bad) + "\n")
            if good:
                out.append("- ✓ " + " · ".join(f"`{g}`" for g in good) + "\n")
    return "".join(out)


def render_rule(path, selector):
    rule = load_rule(path)
    if selector in (None, "", "author"):
        actors = ["author"]
    elif selector == "reviewers":
        actors = [a for a in actors_of(rule) if a != "author"]
    else:
        actors = [selector]
    parts = [render_block(rule, a) for a in actors]
    return "\n".join(p for p in parts if p)


def grep_script(rules_dir):
    """Every text grep of every rule, as the bash block the Mechanical Gate's Part C used to hold."""
    lines = ["```bash", "# Run each grep against the paper's text. Every hit is inspected; the comment gives the rule's own verb and the fix.", ""]
    files = sorted(glob.glob(os.path.join(rules_dir, "*.yml")),
                   key=lambda p: (re.sub(r"\d+.*", "", os.path.basename(p)), int(re.sub(r"\D", "", os.path.basename(p).split("-")[0]) or 0)))
    for path in files:
        rule = load_rule(path)
        greps = [g for g in rule.get("grep") or [] if not g.get("target")]
        if not greps:
            continue
        for g in greps:
            label = f"{rule['id']}: {rule['title']}"
            tail = " · ".join(x for x in (g.get("action"), g.get("hint")) if x)
            lines.append(f"# ── {label}" + (f" ({tail})" if tail else "") + " ──")
            flags = "-rn" + ("i" if "i" in (g.get("flags") or "") else "") + "E"
            pat = g["pattern"].replace("'", "'\\''")
            dashes = " --" if pat.startswith("-") else ""
            lines.append(f"grep {flags}{dashes} '{pat}'")
        lines.append("")
    lines.append("```")
    return "\n".join(lines) + "\n"


def expand(path, stack=()):
    path = os.path.realpath(path)
    if path in stack:
        chain = " -> ".join(stack + (path,))
        sys.exit(f"include cycle: {chain}")
    try:
        with open(path, encoding="utf-8", newline="") as f:  # keep line endings as they are
            lines = f.readlines()
    except OSError as e:
        where = f" (included from {stack[-1]})" if stack else ""
        sys.exit(f"cannot read {path}{where}: {e.strerror}")

    out = []
    fence = None
    for line in lines:
        m = FENCE.match(line)
        if m:
            if fence is None:
                fence = m.group(1)
            elif m.group(1) == fence:
                fence = None
            out.append(line)
            continue
        if not fence and line.strip() == "@@grep-script":
            rules_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "rules")
            out.append(grep_script(rules_dir))
            continue
        m = None if fence else INCLUDE.match(line)
        if m:
            target = m.group(1).replace("\\ ", " ")
            selector = None
            if ".yml#" in target:
                target, selector = target.rsplit("#", 1)
            if not os.path.isabs(target):
                target = os.path.join(os.path.dirname(path), target)
            if target.endswith(".yml"):
                if not os.path.exists(target):
                    sys.exit(f"cannot read {target} (included from {path})")
                out.append(render_rule(target, selector))
            else:
                out.append(expand(target, stack + (path,)))
        else:
            out.append(line)
    return "".join(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.stdout.write(expand(sys.argv[1]))

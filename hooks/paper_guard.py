#!/usr/bin/env python3
"""Enforcement hooks for the paper-writing skill (see README.md, "Enforced rules").

One script, one subcommand per hook event. Claude Code passes the event as JSON on stdin.

  mark     skill frontmatter, PreToolUse (once): records this session as a /paper-writing session
  bash     settings, PreToolUse Bash: refuses commands that write files and name a .tex file, and
           shell reads (cat, head, ...) of the style-example articles
  edit     settings, PreToolUse Write|Edit|MultiEdit|NotebookEdit: guards .tex files in the project
  compact  settings, PostCompact: records that the session was compacted

Every rule applies only in sessions where /paper-writing was invoked. Subagent tool calls carry the
parent's session_id plus an agent_id, so they inherit the session's rules; the main agent's calls
carry no agent_id.

"Has the main agent read the style examples?" is answered from the session transcript: every
article line of at least MIN_LINE chars must appear somewhere in it. The transcript's structure is
not parsed, only searched, so any way of reading that put the text in context counts, and a shell
read that was cut to a preview does not.
"""
import fcntl
import hashlib
import json
import os
import re
import shlex
import sys
import time
from contextlib import contextmanager

STATE_DIR = os.path.join(
    os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state"),
    "paper-writing-skill",
)
STYLE_DIR = "style-examples"
NOT_EXAMPLES = {"MANIFEST.md", "README.md"}
MIN_LINE = 40  # shorter lines (headings, blank lines) are too common to prove anything
STRAY_MATCHES = 3  # found lines this few, between missing ones, are reported as one missing range
STATE_MAX_AGE_DAYS = 30

# A filename ending in .tex: a filename character, then ".tex", then not a letter or digit.
# Matches main.tex, sections/*.tex, $f.tex; not \texttt, latex, context, .text, .texinfo, usetex.
TEX_NAME = re.compile(r"[\w*?\]}$-]\.tex(?![A-Za-z0-9_])")

# Ways a shell command writes files. Checked after quoted strings are removed, so a ">" inside a
# grep pattern does not count. Heredocs are checked on the raw command.
HEREDOC = re.compile(r"<<")
HARMLESS_REDIRECTS = re.compile(r"\d*>&\d|&>\s*/dev/null|\d*>>?\s*/dev/(null|stderr|stdout)")
WRITE_OPS = re.compile(
    r">"                                              # > and >>
    r"|\btee\b(?!\s+/dev/(stderr|stdout|null)\b)"
    r"|\bsed\b[^|;&]*\s-[a-zA-Z]*i"                   # sed -i, sed -Ei, sed -n -i
    r"|\bperl\b[^|;&]*\s-[a-zA-Z]*[ie]"               # perl -i, perl -pi, perl -e
    r"|\b(python[\d.]*|node|ruby)\b[^|;&]*\s-[a-zA-Z]*[ce]?(\s|$)"  # python -c / python - / -I -
    r"|\b(cp|mv|rm|truncate|dd|install|ln)\b"
)

# Programs that print a file's contents. grep, wc, ls and diff are not here: they stay allowed.
SHELL_READERS = {"cat", "head", "tail", "less", "more", "sed", "awk", "gawk", "nl", "tac", "bat",
                 "batcat", "strings", "xxd", "od"}

MSG_BASH = (
    "A .tex filename ({name}) appears in a command that writes files. In a /paper-writing session "
    ".tex files are changed only with the Write or Edit tool. Retry with the Write or Edit tool."
)
MSG_SHELL_READ = (
    "Reading {path} through the shell is blocked in a /paper-writing session: shell output over "
    "30,000 characters is cut to a short preview, so the article would not reach the context. "
    "Read style examples with the Read tool."
)
MSG_SUBAGENT = (
    "Edit of {path} blocked: in a /paper-writing session only the main agent edits .tex files; "
    "subagents may not."
)
MSG_COMPACTED = (
    "Edit of {path} blocked: this session has been compacted, and the paper-writing rules block "
    ".tex edits after compaction (the style examples read earlier are no longer in context)."
)


# ── state ────────────────────────────────────────────────────────────────────

def state_path(session_id):
    return os.path.join(STATE_DIR, re.sub(r"[^\w-]", "_", session_id) + ".json")


@contextmanager
def session_state(session_id):
    """Locked read-modify-write of one session's state."""
    os.makedirs(STATE_DIR, exist_ok=True)
    path = state_path(session_id)
    with open(path + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            with open(path) as f:
                state = json.load(f)
        except (OSError, ValueError):
            state = {}
        before = json.dumps(state, sort_keys=True)
        yield state
        if json.dumps(state, sort_keys=True) != before:
            tmp = path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(state, f)
            os.replace(tmp, path)


def peek_state(session_id):
    try:
        with open(state_path(session_id)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def prune_old_state():
    cutoff = time.time() - STATE_MAX_AGE_DAYS * 86400
    try:
        for name in os.listdir(STATE_DIR):
            p = os.path.join(STATE_DIR, name)
            if os.path.getmtime(p) < cutoff:
                os.remove(p)
    except OSError:
        pass


# ── helpers ──────────────────────────────────────────────────────────────────

def project_dir(event):
    return os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd())


def style_examples(project):
    d = os.path.join(project, STYLE_DIR)
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return None
    return [
        os.path.join(d, n) for n in names
        if not n.startswith(".") and n not in NOT_EXAMPLES and os.path.isfile(os.path.join(d, n))
    ]


def decision(kind, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": kind,
        "permissionDecisionReason": reason,
    }}))


def deny(reason):
    decision("deny", reason)


def shell_segments(cmd):
    """Simple commands of a shell line, as word lists. Falls back to whitespace splitting."""
    try:
        lx = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()")
        lx.whitespace_split = True
        lx.commenters = ""
        segs = [[]]
        for tok in lx:
            if set(tok) <= set(";&|()"):
                segs.append([])
            else:
                segs[-1].append(tok)
    except ValueError:
        segs = [line.split() for line in re.split(r"[;&|\n]", cmd)]
    return [s for s in segs if s]


def article_lines(path):
    """(line number, needle) for each line long enough to prove the article was read.
    Any line ending works: lines are compared by content, with surrounding whitespace trimmed."""
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    out = []
    for n, line in enumerate(re.split(r"\r\n|\r|\n", text), 1):
        line = line.strip()
        if len(line) >= MIN_LINE:
            out.append((n, line))
    return out, hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()


def in_transcript(line, text):
    # The transcript stores tool output inside JSON strings, so quotes, backslashes and tabs appear
    # escaped there. Try the escaped form, then the line as written.
    escaped = json.dumps(line, ensure_ascii=False)[1:-1]
    return escaped in text or (escaped != line and line in text)


def line_ranges(runs):
    """[[3, 5], [9, 9]] -> '3-5, 9'"""
    return ", ".join(f"{a}-{b}" if a != b else str(a) for a, b in runs)


# ── subcommands ──────────────────────────────────────────────────────────────

def cmd_mark(event):
    with session_state(event["session_id"]) as s:
        s["paper_session"] = True
    prune_old_state()


def cmd_bash(event):
    if not peek_state(event["session_id"]).get("paper_session"):
        return
    cmd = event.get("tool_input", {}).get("command", "")

    # Rule 1: a command that writes files may not name a .tex file.
    m = TEX_NAME.search(cmd)
    if m:
        name = re.search(r"[^\s'\"=<>|;&()`]*$", cmd[:m.end()]).group(0)
        unquoted = HARMLESS_REDIRECTS.sub(" ", re.sub(r"'[^']*'|\"(\\.|[^\"\\])*\"", "''", cmd))
        if HEREDOC.search(cmd) or WRITE_OPS.search(unquoted):
            return deny(MSG_BASH.format(name=name))

    # Rule 2: no shell reads of the style-example articles.
    style = os.path.join(project_dir(event), STYLE_DIR)
    if STYLE_DIR not in cmd and os.path.realpath(event.get("cwd", "")) != style:
        return
    cwd = os.path.realpath(event.get("cwd") or project_dir(event))
    for words in shell_segments(cmd):
        while words and re.match(r"^[A-Za-z_]\w*=", words[0]):
            words = words[1:]
        if not words:
            continue
        prog = os.path.basename(words[0])
        if prog == "cd" and len(words) > 1:
            cwd = os.path.realpath(os.path.join(cwd, os.path.expanduser(words[1])))
            continue
        if prog not in SHELL_READERS:
            continue
        for arg in words[1:]:
            if arg.startswith("-"):
                continue
            p = os.path.normpath(os.path.join(cwd, os.path.expanduser(arg)))
            is_glob = any(ch in arg for ch in "*?[")
            if (os.path.dirname(p) == style and os.path.basename(p) not in NOT_EXAMPLES
                    and (is_glob or os.path.isfile(p))):
                return deny(MSG_SHELL_READ.format(path=arg))


def cmd_edit(event):
    state = peek_state(event["session_id"])
    if not state.get("paper_session"):
        return
    ti = event.get("tool_input", {})
    path = os.path.realpath(ti.get("file_path") or ti.get("notebook_path") or "")
    project = project_dir(event)
    if not (path.endswith(".tex") and path.startswith(project + os.sep)):
        return
    if event.get("agent_id"):
        return deny(MSG_SUBAGENT.format(path=path))
    if state.get("compacted"):
        return deny(MSG_COMPACTED.format(path=path))

    folder = os.path.join(project, STYLE_DIR)
    examples = style_examples(project)
    if not examples:
        problem = ("does not exist" if not os.path.isdir(folder) else
                   "holds no articles (" + " and ".join(sorted(NOT_EXAMPLES)) + " do not count)")
        return deny(
            f"Edit of {path} blocked: the paper-writing skill requires the main agent to read the "
            f"target venue's example articles (Stage 3 gate) before editing .tex files, and it "
            f"looks for them in {folder}/, which {problem}."
        )

    transcript = event.get("transcript_path") or ""
    try:
        with open(transcript, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        return decision("ask", (
            f"paper_guard could not read the session transcript ({transcript or 'no path given'}: "
            f"{e.strerror or e}), so it cannot check that the style examples in {folder}/ were "
            f"read. Allow this edit of {path}?"
        ))
    end = text.rfind("\n") + 1  # ignore a transcript entry still being written

    missing = []
    with session_state(event["session_id"]) as s:
        seen = s.setdefault("articles", {})
        for ex in examples:
            lines, sig = article_lines(ex)
            rec = seen.get(ex)
            if not rec or rec.get("sig") != sig:
                rec = {"sig": sig, "offset": 0, "found": []}  # first check, or the article changed
            found = set(rec["found"])
            new_text = text[rec["offset"]:end]
            for n, line in lines:
                if n not in found and in_transcript(line, new_text):
                    found.add(n)
            rec["found"], rec["offset"] = sorted(found), end
            seen[ex] = rec
            # Missing lines as ranges. A few stray matches (a line quoted elsewhere in the
            # session) inside an unread stretch don't split it.
            runs, since_missing = [], None
            for n, _ in lines:
                if n not in found:
                    if runs and since_missing is not None and since_missing <= STRAY_MATCHES:
                        runs[-1][1] = n
                    else:
                        runs.append([n, n])
                    since_missing = 0
                elif since_missing is not None:
                    since_missing += 1
            if runs:
                shown = line_ranges(runs[:6]) + (", ..." if len(runs) > 6 else "")
                missing.append(f"{os.path.basename(ex)}: lines {shown} not in context")
    if missing:
        return deny(
            f"Edit of {path} blocked: the paper-writing skill requires the main agent to have every "
            f"style example in {folder}/ in its context, read in full with the Read tool (Stage 3 "
            "gate), before editing .tex files. Not found in this session's context:\n  "
            + "\n  ".join(missing)
        )


def cmd_compact(event):
    if event.get("agent_id"):
        return
    with session_state(event["session_id"]) as s:
        s["compacted"] = True


COMMANDS = {"mark": cmd_mark, "bash": cmd_bash, "edit": cmd_edit, "compact": cmd_compact}

if __name__ == "__main__":
    try:
        event = json.load(sys.stdin)
        COMMANDS[sys.argv[1]](event)
    except Exception as e:  # a broken guard must not wedge the session
        msg = f"paper_guard.py {' '.join(sys.argv[1:])} failed: {type(e).__name__}: {e}"
        print(msg, file=sys.stderr)
        if sys.argv[1:2] == ["edit"]:  # don't let a crash silently skip the .tex checks
            decision("ask", msg + ". The .tex edit checks did not run. Allow this edit?")
    sys.exit(0)

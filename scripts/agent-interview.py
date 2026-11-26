#!/usr/bin/env python3
"""Interview one Claude Code agent: send an opening message, then one question at a time in the
same session, appending every answer to one report as it goes.

One `claude -p` process runs the whole interview (`--input-format stream-json`): the script
writes one message, waits for that turn's result, appends it to the report, then writes the next.
The agent never sees a question before it is asked. Run two interviews at once by starting this
script twice; each is its own process and session.

What the agent is given: the agent definition, and Claude Code's own system prompt. Settings come
from the user and project sources only (`--setting-sources user,project`), so
`.claude/settings.local.json` is not loaded, while the project's hooks still
apply. `--strict-mcp-config` with no MCP config skips every MCP
server. `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS=1` is set for the agent's process.

Usage (from anywhere; the agent runs in --cwd, the paper's folder, default the current folder):
  python3 scripts/agent-interview.py --agents AGENTS.json --agent NAME --cwd PAPER \
      --opening OPENING.md --questions QUESTIONS.md --report REPORT.md \
      [--model sonnet] [--effort high] [--permission-mode auto]
  Follow-up with the same reviewer (same --agents and --agent; the session ID is in the report):
  python3 scripts/agent-interview.py --agents AGENTS.json --agent NAME --cwd PAPER --resume SESSION_ID \
      --questions FOLLOWUP.md --report REPORT.md

AGENTS.json  the agent definition, as `claude --agents` takes it:
             {"NAME": {"description": "...", "prompt": "...", "tools": [...], "model": "..."}}
OPENING.md   the first message (for a reviewer: "read the section and the article; report
             nothing yet").
QUESTIONS.md the questions, separated by lines holding only `---`; asked in order.
REPORT.md    appended to after every turn (created if missing), so a stopped run keeps every
             answer it got.

Stops at the first failed turn (an error result, or the process ending early) and writes the
error into the report. The `claude` binary is $CLAUDE_BIN, else `claude` on PATH, else the newest
one bundled with the VS Code extension.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def claude_bin():
    if os.environ.get("CLAUDE_BIN"):
        return os.environ["CLAUDE_BIN"]
    if shutil.which("claude"):
        return shutil.which("claude")
    found = sorted(glob.glob(os.path.expanduser(
        "~/.vscode-server/extensions/anthropic.claude-code-*/resources/native-binary/claude")))
    if not found:
        sys.exit("no claude binary: set CLAUDE_BIN or install the CLI")
    return found[-1]


def append(report, text):
    with open(report, "a", encoding="utf-8") as f:
        f.write(text)


def ask(proc, message):
    """Send one user message; return (the turn's result event, or None if the process ended; seconds)."""
    start = time.time()
    proc.stdin.write(json.dumps({"type": "user",
                                 "message": {"role": "user", "content": message}}) + "\n")
    proc.stdin.flush()
    for line in proc.stdout:
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result":
            return ev, time.time() - start
    return None, time.time() - start


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--agents", help="agent definitions as JSON; omit for an agent in .claude/agents/")
    ap.add_argument("--agent", required=True)
    ap.add_argument("--cwd", default=".", help="the folder the agent runs in (the paper's folder)")
    ap.add_argument("--opening", help="the first message; omit with --resume")
    ap.add_argument("--resume", metavar="SESSION_ID",
                    help="continue that interview (its ID is in the report) with these questions")
    ap.add_argument("--questions", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--permission-mode", default="auto")
    args = ap.parse_args()
    report = Path(args.report).resolve()

    if bool(args.opening) == bool(args.resume):
        ap.error("give --opening for a new interview, or --resume SESSION_ID to continue one")
    first = [] if args.resume else [Path(args.opening).read_text(encoding="utf-8").strip()]
    questions = [q.strip() for q in
                 Path(args.questions).read_text(encoding="utf-8").split("\n---\n") if q.strip()]

    cmd = [claude_bin(), "-p", "--input-format", "stream-json", "--output-format", "stream-json",
           "--verbose", *(["--agents", str(Path(args.agents).resolve())] if args.agents else []),
           "--agent", args.agent,
           "--setting-sources", "user,project", "--strict-mcp-config",
           "--permission-mode", args.permission_mode,
           "--model", args.model, "--effort", args.effort]
    if args.resume:
        cmd += ["--resume", args.resume]
    env = dict(os.environ, CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS="1")
    stderr_path = report.with_suffix(".stderr.txt")
    with open(stderr_path, "w") as stderr:
        proc = subprocess.Popen(cmd, cwd=Path(args.cwd).resolve(), env=env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=stderr, text=True, bufsize=1)

        kind = f"Follow-up to session {args.resume}" if args.resume else "Interview"
        append(report, f"# {kind}: {args.agent} ({args.model}, effort {args.effort}, "
                       f"{time.strftime('%Y-%m-%d %H:%M')})\n\n")
        for n, msg in enumerate(first + questions, start=0 if first else 1):
            title = "Opening" if n == 0 else f"Question {n} of {len(questions)}"
            append(report, f"## {title}\n\n> " + msg.replace("\n", "\n> ") + "\n\n")
            ev, secs = ask(proc, msg)
            if ev is None or ev.get("is_error"):
                why = "the process ended" if ev is None else f"error result: {ev.get('result', '')}"
                append(report, f"**Stopped: this turn failed ({why}).** See {stderr_path}.\n")
                proc.kill()
                sys.exit(f"turn {n} failed; see {report}")
            u = ev.get("usage") or {}
            append(report, f"{(ev.get('result') or '').strip()}\n\n"
                           f"*({secs:.0f} s; tokens in {u.get('input_tokens', '?')}, cache read "
                           f"{u.get('cache_read_input_tokens', '?')}, cache write "
                           f"{u.get('cache_creation_input_tokens', '?')}, out "
                           f"{u.get('output_tokens', '?')}; session {ev.get('session_id')})*\n\n")
            print(f"{title}: done in {secs:.0f} s", flush=True)
        proc.stdin.close()
        proc.wait(timeout=60)
    print(f"report: {report}")


if __name__ == "__main__":
    main()

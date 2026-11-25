#!/usr/bin/env python3
"""bash-guard PreToolUse hook for Bash: blocks commands that may modify a project's protected files.

A project opts in with .paper-writing/bash-guard.json (an empty "protected" list protects nothing).
The project is found from $CLAUDE_PROJECT_DIR, else by walking up from the command's folder.
Each project seen is recorded for the Python runtime hook (runtime.py), which guards writes made
from inside Python processes that Bash commands start.

Claude Code passes the event as JSON on stdin. A block is a permissionDecision "deny" with the
reason shown to Claude. A crash in this hook allows the command (and prints the error to stderr),
so a broken guard cannot stop every Bash call.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
CONFIG = os.path.join(".paper-writing", "bash-guard.json")


def norm(path):  # see checkperms.norm
    return os.path.realpath(path)


def find_config(event):
    starts = [os.environ.get("CLAUDE_PROJECT_DIR"), event.get("cwd")]
    for start in starts:
        d = norm(start) if start else None
        while d:
            path = os.path.join(d, CONFIG)
            if os.path.isfile(path):
                return path
            parent = os.path.dirname(d)
            d = parent if parent != d else None
    return None


def main():
    event = json.load(sys.stdin)
    if event.get("tool_name") != "Bash":
        return
    config = find_config(event)
    if not config:
        return
    import checkperms
    checkperms.register_project(config)
    project = checkperms.Project(config)
    if not project.paths and not project.globs:
        return
    command = event.get("tool_input", {}).get("command", "")
    ok, reason = checkperms.check(command, event.get("cwd") or os.getcwd(), project)
    if not ok:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": checkperms.block_message(reason, project),
        }}))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never wedge the session on a guard bug
        print(f"bash-guard pretooluse.py failed: {type(e).__name__}: {e}", file=sys.stderr)
    sys.exit(0)

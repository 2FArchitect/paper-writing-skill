#!/usr/bin/env python3
"""Run bash-guard's checker over test files.

  run_tests.py [--config CONFIG] [--report OUT.jsonl] FILE.jsonl ...

Each line of a test file is a JSON object:
  {"cmd": "...", "expect": "allow" | "block", "cwd": "...", "note": "..."}
"expect" is optional: lines without it are only run (use --report to save the verdicts for review).
"cwd" is optional; a relative cwd is taken from the project root, and the default is the root.

The default config is tests/fixture/.paper-writing/bash-guard.json, a synthetic project.
Python interpreters count as guarded for the run (the runtime hook is tested separately).
Exit status 1 if any expectation failed.
"""
import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(HERE, "fixture", ".paper-writing", "bash-guard.json"))
    ap.add_argument("--report")
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()

    # Make the running interpreter count as guarded, without touching the real state folder.
    state = tempfile.mkdtemp(prefix="bash-guard-test-")
    os.makedirs(os.path.join(state, "paper-writing-skill"))
    with open(os.path.join(state, "paper-writing-skill", "bash-guard-pythons.json"), "w") as f:
        json.dump([os.path.realpath(sys.executable)], f)
    os.environ["XDG_STATE_HOME"] = state
    import checkperms
    checkperms.GUARDED_PYTHONS = os.path.join(state, "paper-writing-skill", "bash-guard-pythons.json")

    project = checkperms.Project(a.config)
    failed = total = 0
    report = open(a.report, "w") if a.report else None
    for path in a.files:
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                t = json.loads(line)
                cwd = os.path.join(project.root, t.get("cwd") or "")
                ok, reason = checkperms.check(t["cmd"], cwd, project)
                verdict = "allow" if ok else "block"
                total += 1
                if report:
                    report.write(json.dumps({**t, "verdict": verdict, "reason": reason}) + "\n")
                if any(ord(c) < 32 and c not in "\n\t" for c in reason):
                    failed += 1
                    print(f"FAIL {os.path.basename(path)}:{n} control character in the reason: {reason!r}")
                if t.get("expect") and t["expect"] != verdict:
                    failed += 1
                    print(f"FAIL {os.path.basename(path)}:{n} expected {t['expect']}, got {verdict}"
                          f"{': ' + reason if reason else ''}\n     {t['cmd'][:300]}")
    if report:
        report.close()
    print(f"{total} commands, {failed} failed expectations")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

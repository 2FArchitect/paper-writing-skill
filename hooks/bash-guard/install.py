#!/usr/bin/env python3
"""Install bash-guard's Python runtime hook into this machine's Python interpreters.

  install.py [--quiet] [--python EXE ...] [--project CONFIG] [--uninstall]

For each interpreter (default: python3, python and python3.N found on PATH, plus /usr/bin/python3
and /usr/local/bin/python3), writes a one-line .pth file into its site-packages folder. At startup
Python runs that line, which loads runtime.py when CLAUDECODE=1 (set by Claude Code for its Bash
commands). The line is checked to load, and each interpreter where it does is recorded as guarded;
checkperms.py allows Python on protected paths only for recorded interpreters.

A site-packages folder the user cannot write is written with 'sudo -n' (no password prompt); if that
fails the interpreter is reported and left unguarded. Safe to re-run: files are rewritten only when
their content changed. Run by setup and, once per session, when /paper-writing starts (container
rebuilds remove site-packages changes).
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
RUNTIME = os.path.join(HERE, "runtime.py")
PTH_NAME = "paper_writing_bash_guard.pth"
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import checkperms  # noqa: E402

PTH_LINE = (
    "import os; exec(compile(open(P).read(), P, 'exec'), {'__file__': P, '__name__': "
    "'bash_guard_runtime'}) if os.environ.get('CLAUDECODE') == '1' and os.path.exists(P) else None"
)

# A virtual environment's python is a symlink to a base interpreter but has its own site-packages,
# so it is recorded by its own path; a base interpreter by its real path (see checkperms.python_key).
PROBE = ("import json, os, site, sys; venv = sys.prefix != sys.base_prefix; "
         "print(json.dumps([os.path.abspath(sys.executable) if venv else os.path.realpath(sys.executable), "
         "site.getsitepackages()]))")


def candidates():
    found = []
    for d in os.environ.get("PATH", "").split(os.pathsep):
        for pattern in ("python3", "python", "python3.[0-9]*"):
            for exe in glob.glob(os.path.join(d, pattern)):
                if os.path.basename(exe).replace(".", "").replace("python", "").isdigit() or \
                        os.path.basename(exe) in ("python3", "python"):
                    found.append(exe)
    found += ["/usr/bin/python3", "/usr/local/bin/python3"]
    return [e for e in found if os.path.isfile(e) and os.access(e, os.X_OK)]


def write_file(path, content):
    """Write content to path (with sudo -n if needed); True if it is in place afterwards."""
    try:
        with open(path, encoding="utf-8") as f:
            if f.read() == content:
                return True
    except OSError:
        pass
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except PermissionError:
        r = subprocess.run(["sudo", "-n", "tee", path], input=content.encode(), capture_output=True)
        return r.returncode == 0


def remove_file(path):
    if not os.path.exists(path):
        return True
    try:
        os.remove(path)
        return True
    except PermissionError:
        return subprocess.run(["sudo", "-n", "rm", "-f", path], capture_output=True).returncode == 0


def probe(exe):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    r = subprocess.run([exe, "-I", "-c", PROBE], capture_output=True, text=True, env=env, timeout=30)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


def loads(exe):
    """Does the runtime hook load in this interpreter when CLAUDECODE=1?"""
    env = dict(os.environ, CLAUDECODE="1")
    r = subprocess.run([exe, "-I", "-c", "import sys; print('_bash_guard_active' in sys.modules)"],
                       capture_output=True, text=True, env=env, timeout=30)
    return r.stdout.strip() == "True"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quiet", action="store_true", help="print only problems")
    ap.add_argument("--python", nargs="+", help="interpreters to handle (default: found on PATH)")
    ap.add_argument("--project", help="also register this project's bash-guard.json")
    ap.add_argument("--uninstall", action="store_true")
    a = ap.parse_args()

    say = (lambda *_: None) if a.quiet else print
    if a.project:
        checkperms.register_project(a.project)
    content = ("# bash-guard (paper-writing skill): loads runtime.py in Claude Code Bash commands\n"
               + PTH_LINE.replace("import os; ", f"import os; P = {RUNTIME!r}; ") + "\n")

    guarded, seen, problems = set(), set(), []
    for exe in a.python or candidates():
        info = probe(exe)
        if not info:
            problems.append(f"{exe}: could not run it")
            continue
        real, sites = info
        if real in seen:
            continue
        seen.add(real)
        sites = [s for s in sites if os.path.isdir(s)]
        if not sites:
            problems.append(f"{exe}: no site-packages folder")
            continue
        pth = os.path.join(sites[0], PTH_NAME)
        if a.uninstall:
            if remove_file(pth):
                say(f"removed {pth}")
            else:
                problems.append(f"could not remove {pth}")
            continue
        if not write_file(pth, content):
            problems.append(f"{real}: could not write {pth} (not writable, and 'sudo -n' failed)")
            continue
        if loads(exe):
            guarded.add(real)
            say(f"guarded: {real} ({pth})")
        else:
            problems.append(f"{real}: wrote {pth}, but the runtime hook did not load")

    os.makedirs(checkperms.STATE_DIR, exist_ok=True)
    previous = checkperms.guarded_pythons()
    keep = set() if a.uninstall else {p for p in previous if p not in seen}
    with open(checkperms.GUARDED_PYTHONS, "w", encoding="utf-8") as f:
        json.dump(sorted(keep | guarded), f, indent=1)
    for p in problems:
        print(f"bash-guard install: {p}", file=sys.stderr)
    return 1 if problems and not guarded and not a.uninstall else 0


if __name__ == "__main__":
    sys.exit(main())

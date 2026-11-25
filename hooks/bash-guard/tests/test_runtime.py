#!/usr/bin/env python3
"""Test bash-guard's Python runtime hook end to end, without touching the real system.

Builds a throwaway project and virtual environment in a temp folder, installs the hook into the
venv with install.py (state kept in the temp folder), then runs Python snippets in the venv with
CLAUDECODE=1 and checks which are blocked. Exit status 1 if any case fails.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.realpath(__file__))
GUARD = os.path.dirname(HERE)

tmp = tempfile.mkdtemp(prefix="bash-guard-runtime-")
proj = os.path.join(tmp, "proj")
for d in ("paper/source", "tools", ".paper-writing", "out"):
    os.makedirs(os.path.join(proj, d))
for f in ("paper/source/a.tex", "paper/source/refs.bib"):
    with open(os.path.join(proj, f), "w") as fh:
        fh.write("original\n")
config = os.path.join(proj, ".paper-writing", "bash-guard.json")
with open(config, "w") as fh:
    json.dump({"protected": ["../paper/source"],
               "writers": {"../tools/sync.py": ["../paper/source/refs.bib"]}}, fh)
with open(os.path.join(proj, "tools", "sync.py"), "w") as fh:
    fh.write("import sys\nopen(sys.argv[1], 'a').write('synced\\n')\nprint('ok')\n")

venv = os.path.join(tmp, "venv")
subprocess.run([sys.executable, "-m", "venv", "--without-pip", venv], check=True)
py = os.path.join(venv, "bin", "python")
env = dict(os.environ, XDG_STATE_HOME=os.path.join(tmp, "state"))
env.pop("CLAUDECODE", None)
r = subprocess.run([sys.executable, os.path.join(GUARD, "install.py"), "--python", py, "--project", config],
                   env=env, capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip())
if r.returncode:
    sys.exit("install failed")

guarded_env = dict(env, CLAUDECODE="1")
A, BIB = "paper/source/a.tex", "paper/source/refs.bib"
cases = [
    ("read", f"print(open('{A}').read() and 'ok')", "allow"),
    ("Path.read_text", f"import pathlib; pathlib.Path('{A}').read_text(); print('ok')", "allow"),
    ("open w", f"open('{A}', 'w')", "block"),
    ("open a", f"open('{A}', 'a')", "block"),
    ("open r+", f"open('{A}', 'r+')", "block"),
    ("new file in protected folder", "open('paper/source/new.txt', 'w')", "block"),
    ("os.open O_WRONLY", f"import os; os.open('{A}', os.O_WRONLY)", "block"),
    ("Path.write_text", f"import pathlib; pathlib.Path('{A}').write_text('x')", "block"),
    ("os.replace onto", f"import os; open('out/t','w').close(); os.replace('out/t', '{A}')", "block"),
    ("os.rename away", f"import os; os.rename('{A}', 'out/moved')", "block"),
    ("os.remove", f"import os; os.remove('{A}')", "block"),
    ("shutil.copy into", f"import shutil; shutil.copy('tools/sync.py', '{A}')", "block"),
    ("shutil.copy out", f"import shutil; shutil.copy('{A}', 'out/copy.tex'); print('ok')", "allow"),
    ("fileinput inplace", f"import fileinput\nfor l in fileinput.input('{A}', inplace=True): print(l, end='')", "block"),
    ("write elsewhere", "open('out/x.txt', 'w').write('x'); print('ok')", "allow"),
    ("subprocess sed -i", f"import subprocess; subprocess.run(['sed', '-i', 's/o/0/', '{A}'])", "block"),
    ("subprocess grep", f"import subprocess; subprocess.run(['grep', '-c', 'o', '{A}'], check=True); print('ok')", "allow"),
    ("shell=True sed -i", f"import subprocess; subprocess.run('sed -i s/o/0/ {A}', shell=True)", "block"),
    ("os.system sed -i", f"import os; os.system('sed -i s/o/0/ {A}')", "block"),
    ("child python write", f"import subprocess, sys; r = subprocess.run([sys.executable, '-c', \"open('{A}','w')\"], capture_output=True, text=True); print('blocked-in-child' if 'bash-guard blocked' in r.stderr else 'ok')", "child"),
]
failed = 0
for name, code, expect in cases:
    r =subprocess.run([py, "-c", code], cwd=proj, env=guarded_env, capture_output=True, text=True)
    blocked = "bash-guard blocked" in r.stderr
    got = "block" if blocked else ("child" if "blocked-in-child" in r.stdout else
                                   "allow" if r.returncode == 0 and "ok" in r.stdout else "error")
    status = "ok  " if got == expect else "FAIL"
    failed += got != expect
    print(f"{status} {name:30} expected {expect:6} got {got}" + ("" if got == expect else f"\n     {r.stderr.strip()[-400:]}"))

# Writer scripts: allowed to write their own files only.
for target, expect in ((BIB, "allow"), (A, "block")):
    r = subprocess.run([py, "tools/sync.py", target], cwd=proj, env=guarded_env, capture_output=True, text=True)
    got = "block" if "bash-guard blocked" in r.stderr else ("allow" if r.returncode == 0 else "error")
    failed += got != expect
    print(f"{'ok  ' if got == expect else 'FAIL'} {'writer script -> ' + target:30} expected {expect:6} got {got}")

# Without CLAUDECODE the hook is not loaded.
r = subprocess.run([py, "-c", f"open('{A}', 'a').write(''); print('ok')"], cwd=proj, env=env, capture_output=True, text=True)
got = "allow" if r.returncode == 0 else "block"
failed += got != "allow"
print(f"{'ok  ' if got == 'allow' else 'FAIL'} {'not a Claude Code command':30} expected allow  got {got}")

with open(os.path.join(proj, A)) as fh:
    content = fh.read()
print("a.tex unchanged:", content == "original\n")
failed += content != "original\n"
print(f"{failed} failed")
import shutil  # noqa: E402
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if failed else 0)

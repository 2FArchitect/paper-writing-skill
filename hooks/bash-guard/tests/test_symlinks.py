"""Symlink tests: a link outside the project pointing into a protected folder. The fixture's
protected folders need not exist for the other tests, so this test creates real folders and a link
in a temp project and runs the checker directly."""
import json, os, sys, tempfile

GUARD = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, GUARD)
sys.dont_write_bytecode = True
import checkperms

tmp = tempfile.mkdtemp(prefix="bash-guard-link-")
os.makedirs(os.path.join(tmp, "proj", "paper", "source"))
os.makedirs(os.path.join(tmp, "proj", ".paper-writing"))
with open(os.path.join(tmp, "proj", ".paper-writing", "bash-guard.json"), "w") as f:
    json.dump({"protected": ["../paper/source"]}, f)
link = os.path.join(tmp, "link")
os.symlink(os.path.join(tmp, "proj", "paper", "source"), link)
project = checkperms.Project(os.path.join(tmp, "proj", ".paper-writing", "bash-guard.json"))
cases = [
    (f"sed -i s/a/b/ {link}/main.tex", False),
    (f"echo x > {link}/new.txt", False),
    (f"grep -c a {link}/main.tex", True),
]
failed = 0
for cmd, want in cases:
    ok, reason = checkperms.check(cmd, os.path.join(tmp, "proj"), project)
    print("ok  " if ok == want else "FAIL", cmd.replace(tmp, "$TMP"), "->", "allow" if ok else "block")
    failed += ok != want
import shutil
shutil.rmtree(tmp)
sys.exit(1 if failed else 0)

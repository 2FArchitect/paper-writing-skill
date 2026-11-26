#!/usr/bin/env python3
"""Check rules/*.yml (or the folder given, e.g. a project's .paper-writing/rules): parse, required keys, actor shape, and that each rule's bad examples match its
grep patterns while its good examples do not (examples double as regex tests). Exit 1 on any error."""
import glob, os, re, sys
import yaml

META = {"id", "title", "severity", "applies", "merged", "source", "exceptions", "grep", "grep_hits_only", "notes"}
ACTOR_KEYS = {"text", "questions", "why", "examples"}
root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rules")
errors, warnings = [], []

def compile_greps(rule):
    out = []
    for g in rule.get("grep") or []:
        flags = re.I if "i" in (g.get("flags") or "") else 0
        try:
            out.append(re.compile(g["pattern"], flags | re.M))
        except re.error as e:
            errors.append(f"{rule['id']}: bad regex {g['pattern']!r}: {e}")
    return out

for path in sorted(glob.glob(os.path.join(root, "*.yml"))):
    name = os.path.basename(path)
    try:
        rule = yaml.safe_load(open(path, encoding="utf-8"))
    except yaml.YAMLError as e:
        errors.append(f"{name}: YAML error: {e}"); continue
    rid = rule.get("id")
    if not rid or not name.startswith(rid + "-"):
        errors.append(f"{name}: id {rid!r} does not match the file name")
    if not rule.get("source"):
        errors.append(f"{name}: no source")
    actors = {k: v for k, v in rule.items() if k not in META}
    if not actors:
        errors.append(f"{name}: no actor block")
    for a, block in actors.items():
        if not isinstance(block, dict):
            errors.append(f"{name}: actor {a} is not a mapping"); continue
        extra = set(block) - ACTOR_KEYS
        if extra:
            errors.append(f"{name}: actor {a} has unknown keys {sorted(extra)}")
        if not (block.get("text") or block.get("questions")):
            errors.append(f"{name}: actor {a} has neither text nor questions")
        if not block.get("why"):
            warnings.append(f"{name}: actor {a} has no why")
    for g in rule.get("grep") or []:
        extra = set(g) - {"pattern", "flags", "target", "action", "hint"}
        if extra:
            errors.append(f"{name}: grep entry has unknown keys {sorted(extra)} (an unquoted comma in a flow mapping?)")
    greps = compile_greps(rule)
    if greps:
        for a, block in actors.items():
            ex = (block or {}).get("examples") or {}
            for bad in ex.get("bad") or []:
                if not any(g.search(bad) for g in greps):
                    warnings.append(f"{name}: {a} bad example not matched by any grep: {bad!r}")
            for good in ex.get("good") or []:
                hits = [g.pattern for g in greps if g.search(good)]
                if hits:
                    errors.append(f"{name}: {a} good example matches grep: {good!r}")

for w in warnings: print("warning:", w)
for e in errors: print("ERROR:", e)
print(f"{len(glob.glob(os.path.join(root, '*.yml')))} rule files, {len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)

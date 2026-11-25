#!/usr/bin/env python3
"""Score bash-guard's verdicts against hand-checked ground truth.

  evaluate.py --config CONFIG --verdicts VERDICTS.jsonl --out REPORT.md GROUND.jsonl ...

GROUND files: one JSON object per single command: {"id", "single", "cwd", "label", "writes", "how"}
  label: read | write | runs-code ; writes: absolute paths the command creates, changes or deletes.
VERDICTS: {"single", "verdict": allow|block, "reason", "full"}, matched to the ground truth by the
  single command's text.

A miss is a command that writes a protected path but was allowed. A false block is a command that
writes no protected path (a read, or a write elsewhere) but was blocked. runs-code commands run code
whose writes cannot be known from the command line, so they are counted on their own.
Exit status 1 if there is any miss.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True
import checkperms  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("ground", nargs="+")
    a = ap.parse_args()

    project = checkperms.Project(a.config)
    verdicts = [json.loads(l) for l in open(a.verdicts)]
    ground = {}
    for g in a.ground:
        for l in open(g):
            r = json.loads(l)
            ground[r["id"]] = r
    # Matched by command text: single commands are unique (deduplicated), and the verdict file's
    # order changes when verdicts change.
    by_text = {g["single"]: g for g in ground.values()}
    if len(by_text) != len(ground) or set(by_text) != {v["single"] for v in verdicts}:
        sys.exit("ground truth and verdicts are not for the same set of commands")

    buckets = collections.defaultdict(list)
    for v in verdicts:
        g = by_text[v["single"]]
        hits = [w for w in g["writes"] if project.protects(w)]
        if g["label"] == "runs-code":
            key = f"runs-code, {v['verdict']}"
        elif hits:
            key = "correct block" if v["verdict"] == "block" else "MISS"
        else:
            key = "correct allow" if v["verdict"] == "allow" else "false block"
        buckets[key].append((g, v, hits))

    order = ["MISS", "false block", "correct block", "correct allow", "runs-code, block", "runs-code, allow"]
    summary = {k: len(buckets.get(k, [])) for k in order}
    print(json.dumps(summary))
    with open(a.out, "w") as f:
        f.write(f"# bash-guard vs ground truth ({os.path.basename(a.config)})\n\n")
        for k in order:
            f.write(f"- {k}: {summary[k]}\n")
        for k in ("MISS", "false block", "correct block", "runs-code, allow"):
            items = buckets.get(k, [])
            if not items:
                continue
            f.write(f"\n## {k} ({len(items)})\n\n")
            for g, v, hits in items:
                f.write(f"### id {g['id']}: ground truth {g['label']}" + (f", writes protected {hits}" if hits else "")
                        + f"; checker {v['verdict']}\n\n")
                f.write(f"Ground truth reason: {g['how']}  \nChecker reason: {v['reason'] or '-'}  \ncwd: `{g['cwd']}`\n\n")
                f.write(f"```bash\n{g['single']}\n```\n\n")
    return 1 if summary["MISS"] else 0


if __name__ == "__main__":
    sys.exit(main())

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
"""
import os
import re
import sys

INCLUDE = re.compile(r"^\s*@((?:\\ |\S)+)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


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
        m = None if fence else INCLUDE.match(line)
        if m:
            target = m.group(1).replace("\\ ", " ")
            if not os.path.isabs(target):
                target = os.path.join(os.path.dirname(path), target)
            out.append(expand(target, stack + (path,)))
        else:
            out.append(line)
    return "".join(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.stdout.write(expand(sys.argv[1]))

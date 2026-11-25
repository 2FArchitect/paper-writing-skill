# bash-guard

Blocks Claude Code Bash commands that may modify a project's protected files, so those files are
changed only with the Edit and Write tools. It is meant to catch accidents (a forgotten rule), not
a determined attempt to get around it.

## Turning it on for a project

Create `<project>/.paper-writing/bash-guard.json`. Paths are relative to that file's folder:

```json
{
  "protected": ["../paper/source", "../data"],
  "writers": {"../tools/sync-bib.py": ["../paper/source/refs.bib"]}
}
```

- `protected`: folders and files. An empty list protects nothing; no file means bash-guard is off.
- `writers`: Python scripts allowed to write the listed protected files.

## What it does

1. **Bash hook** (`pretooluse.py`, registered by `setup`). The command is parsed by `shfmt`
   (mvdan/sh, `bin/`). Each simple command that names a protected path (after resolving it against
   the current folder, `cd` included, with variables set earlier in the same command filled in) may
   run only if its program is on the read-only list in `allowlist.json` and no argument matches one
   of that program's exception patterns. A redirection into a protected path is always blocked.
2. **Python runtime hook** (`runtime.py`, installed by `install.py` as a `.pth` file). In Python
   processes started by Bash commands (`CLAUDECODE=1`), an audit hook blocks writes to protected
   paths and launches of programs the Bash check would block. Python is therefore allowed in step 1.

On a block, Claude sees the reason and is told to use the Edit or Write tool, or to ask the user
for an exception if the block was a false positive.

## Known limits

- Scripts run by path (`bash x.sh`), and interpreters other than Python, are checked only by
  their command line.
- Paths computed at run time are recognized only in simple forms.
- Git commands that change the working tree without naming a path (`git cherry-pick`,
  `git checkout <branch>`) are not caught.
- Python C extensions that write files directly are not caught.

## Tests

```bash
python3 tests/run_tests.py tests/synthetic.jsonl   # checker, synthetic cases
python3 tests/test_runtime.py                       # Python runtime hook, in a throwaway venv
python3 tests/test_symlinks.py                      # symlinks into protected folders
python3 tests/evaluate.py --config CFG --verdicts V.jsonl --out R.md GROUND.jsonl   # vs ground truth
```

`tests/local/` is gitignored: put test files made from your own projects' commands there.

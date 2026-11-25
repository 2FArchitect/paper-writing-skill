#!/usr/bin/env python3
"""bash-guard checker: may this shell command run, given a project's protected paths?

The command is parsed by shfmt (mvdan/sh, shipped in bin/). Every simple command in it is checked:

  1. A redirection that writes (>, >>, >|, &>, &>>, <>, >&file) into a protected path is blocked.
  2. A command that names a protected path, runs in a protected folder, uses a variable that holds a
     protected path, or shares a pipeline with such a command, may run only if its program is on the
     read-only allowlist (allowlist.json) and no argument matches one of that program's exceptions.
     Python interpreters are allowed when the runtime hook (runtime.py) is installed in them.
  3. Wrappers (timeout, nohup, env, xargs, ...) are unwrapped; bash -c, sh -c and eval strings, and
     heredocs given to a shell, are parsed and checked the same way.
  4. A command shfmt cannot parse is blocked if its text names a protected path, else allowed.

Library use:  check(command, cwd, project) -> (allowed: bool, reason: str)
Shell use:    checkperms.py --config PROJECT_CONFIG [--cwd DIR] -- COMMAND
              prints the verdict; exit status 0 = allow, 1 = block, 2 = usage or config error.
"""
import json
import os
import re
import subprocess
import sys

# fnmatch and shutil are imported where used: shutil alone costs ~16 ms at every hook start.

HERE = os.path.dirname(os.path.realpath(__file__))
ALLOWLIST = os.path.join(HERE, "allowlist.json")
STATE_DIR = os.path.join(os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state"),
                         "paper-writing-skill")
GUARDED_PYTHONS = os.path.join(STATE_DIR, "bash-guard-pythons.json")
WRITE_REDIRECTS = {">", ">>", ">|", "&>", "&>>", "<>"}
MAX_DEPTH = 8  # nested bash -c / eval levels


class ConfigError(Exception):
    pass


def norm(path):
    """Absolute path with symlinks resolved, so a link into a protected folder is recognized.
    (Each lookup costs a few milliseconds on a Windows-mounted folder; accepted for correctness.)"""
    return os.path.realpath(path)


# ── configuration ────────────────────────────────────────────────────────────

def shfmt_path():
    machine = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}.get(
        os.uname().machine.lower(), os.uname().machine.lower())
    system = os.uname().sysname.lower()
    name = f"shfmt-{system}-{machine}" + (".exe" if system == "windows" else "")
    path = os.path.join(HERE, "bin", name)
    if not os.path.isfile(path):
        raise ConfigError(f"no shfmt binary for this platform: {path} is missing")
    return path


_allowlist = None


def allowlist():
    global _allowlist
    if _allowlist is None:
        with open(ALLOWLIST, encoding="utf-8") as f:
            raw = json.load(f)
        ro = {}
        for prog, spec in raw["read_only"].items():
            if isinstance(spec, list):
                spec = {"except": spec}
            ro[prog] = {"except": [re.compile(p) for p in spec.get("except", [])],
                        "write_operands": spec.get("write_operands"),
                        "value_options": spec.get("value_options", [])}
        _allowlist = {
            "read_only": ro,
            "python_names": re.compile(raw["python"]["names"]),
            "python_except": [re.compile(p) for p in raw["python"]["except"]],
            "wrappers": {k: v for k, v in raw["wrappers"].items() if not k.startswith("_")},
            "shells": set(raw["shells"]),
        }
    return _allowlist


class Project:
    """A project's protected paths and allowed writer scripts, from its bash-guard.json.
    Paths in the file are relative to the file's own folder."""

    def __init__(self, config_path):
        self.config_path = norm(config_path)
        base = os.path.dirname(self.config_path)
        try:
            with open(self.config_path, encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, ValueError) as e:
            raise ConfigError(f"cannot read {self.config_path}: {e}")
        self.root = norm(os.path.join(base, raw.get("project_root", "..")))
        self.paths, self.globs = [], []
        for entry in raw.get("protected", []):
            p = os.path.normpath(os.path.join(base, entry))
            if any(c in entry for c in "*?["):
                self.globs.append(p)
            else:
                self.paths.append(norm(p))
        self.writers = {}
        for script, targets in raw.get("writers", {}).items():
            self.writers[norm(os.path.join(base, script))] = [
                norm(os.path.join(base, t)) for t in targets]
        # Text forms of each protected path that may appear in a command: the absolute path here,
        # and the path relative to the command's current folder, added per check (named_in). Not
        # relative to the project root: 'paper/source' run in another folder names that folder's
        # paper/source, not the project's.
        self.texts = set(self.paths)
        # For a glob entry, the literal text after its last wildcard (".tex" for "**/*.tex").
        self.glob_tails = [re.split(r"[*?\]]", g)[-1] for g in self.globs]
        self.glob_tails = [t for t in self.glob_tails if len(t) >= 2]

    def protects(self, path):
        """Is this absolute path (no wildcards) protected?"""
        if "\x00" in path:
            return None
        path = norm(path)
        for p in self.paths:
            if path == p or path.startswith(p + os.sep):
                return p
        for g in self.globs:
            if __import__("fnmatch").fnmatch(path, g):
                return g
        return None

    def overlaps(self, pattern):
        """Could this absolute path with wildcards ('*' where the shell expands) reach a protected
        path? True when the text before the first wildcard leads into or onto a protected path."""
        head = re.split(r"[*?\[]", pattern, maxsplit=1)[0]
        for p in self.paths:
            if head.startswith(p + os.sep) or head == p or p.startswith(head):
                return p
        for g in self.globs:
            fnmatch = __import__("fnmatch").fnmatch
            if fnmatch(pattern, g) or fnmatch(head, g):
                return g
        return None

    def named_in(self, text, cwd):
        """Does this raw text name a protected path (absolute, project-relative, cwd-relative, or a
        glob entry's literal tail)?"""
        for t in self.texts:
            if contains_name(text, t):
                return t
        for p in self.paths:
            rel = os.path.relpath(p, cwd)
            if rel not in (".", "..") and not rel.startswith("../..") and contains_name(text, rel):
                return rel
        for t in self.glob_tails:
            if t in text:
                return t
        return None


def contains_name(text, name):
    """Is name in text as a whole path of its own? It must start the text, follow a separator
    (space, quote, = ( , : ; | & < > `) or './', and not continue as a longer name. So
    'paper/source' is in 'cat paper/source/a.tex' and in "open('./paper/source/x')", but not in
    '/x/my-paper/sources' or '/tmp/copy/paper/source'."""
    if name.startswith(os.sep):
        before = r"(?<![\w.-])"
    else:
        before = r"(?:^|(?<=[\s'\"=(,:;|&<>`])|(?<=[\s'\"=(,:;|&<>`]\./)|(?<=^\./))"
    return re.search(before + re.escape(name) + r"(?![\w.-])", text) is not None


PROJECTS = os.path.join(STATE_DIR, "bash-guard-projects.json")


def registered_projects(existing_only=True):
    """Config paths of every project bash-guard has seen (read by the Python runtime hook)."""
    try:
        with open(PROJECTS, encoding="utf-8") as f:
            paths = json.load(f)
    except (OSError, ValueError):
        return []
    return [p for p in paths if os.path.isfile(p)] if existing_only else paths


def register_project(config_path):
    config_path = norm(config_path)
    known = registered_projects(existing_only=False)
    if config_path in known:
        return
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = PROJECTS + f".{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(known + [config_path], f, indent=1)
    os.replace(tmp, PROJECTS)


def python_key(exe):
    """How an interpreter is recorded: a virtual environment's python by its own path (it has its
    own site-packages), any other by its real path."""
    exe = os.path.abspath(exe)
    if os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(exe)), "pyvenv.cfg")):
        return exe
    return os.path.realpath(exe)


def guarded_pythons():
    try:
        with open(GUARDED_PYTHONS, encoding="utf-8") as f:
            return set(json.load(f))
    except (OSError, ValueError):
        return set()


# ── parsing ──────────────────────────────────────────────────────────────────

_parse_cache = {}


def parse(command):
    """shfmt's syntax tree for a command, or None when it cannot be parsed."""
    if command in _parse_cache:
        return _parse_cache[command]
    try:
        r = subprocess.run([shfmt_path(), "--to-json", "-ln", "bash"], input=command.encode("utf-8"),
                           capture_output=True, timeout=10)
        tree = json.loads(r.stdout) if r.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        tree = None
    _parse_cache[command] = tree
    return tree


def unescape(lit):
    return re.sub(r"\\(.)", r"\1", lit, flags=re.S)


UNKNOWN = "\x00"  # stands in for an expansion whose value is not known
PARAM_MODIFIERS = ("Exp", "Repl", "Slice", "Index", "Length", "Excl", "Names", "Width")


def params(node):
    """Names of the variables a word expands."""
    names = set()
    if isinstance(node, dict):
        if node.get("Type") == "ParamExp" and isinstance(node.get("Param"), dict):
            names.add(node["Param"].get("Value", ""))
        for v in node.values():
            names |= params(v)
    elif isinstance(node, list):
        for v in node:
            names |= params(v)
    return names


def is_stmt(node):
    return isinstance(node, dict) and "Type" not in node and ("Cmd" in node or "Redirs" in node)


# ── checking ─────────────────────────────────────────────────────────────────

class Blocked(Exception):
    """A block, with its reason. The UNKNOWN marker never reaches the text: it is shown as '$…'."""

    def __init__(self, reason):
        super().__init__(reason.replace(UNKNOWN, "$…"))


class Checker:
    def __init__(self, command, cwd, project, depth=0, tainted=None, variables=None, functions=None):
        self.src = command.encode("utf-8")
        self.cwd = norm(cwd)
        self.project = project
        self.depth = depth
        self.tainted = set(tainted or ())  # variables holding a protected path
        self.vars = dict(variables or {})  # variables set earlier in the command to a known value
        self.functions = set(functions or ())  # shell functions defined in the command

    # helpers
    def raw(self, node):
        try:
            return self.src[node["Pos"]["Offset"]:node["End"]["Offset"]].decode("utf-8", "replace")
        except (KeyError, TypeError):
            return ""

    def literal(self, word):
        """A word's value with quotes removed. Variables set earlier in the command (or in the
        environment) are filled in; other expansions ($(..), ${x%y}, unknown $x) become UNKNOWN.
        Glob characters stay as typed."""
        out = []
        for part in word.get("Parts", []):
            t = part.get("Type")
            if t == "Lit":
                out.append(unescape(part.get("Value", "")))
            elif t == "SglQuoted":
                out.append(part.get("Value", ""))
            elif t == "DblQuoted":
                out.append(self.literal(part))
            elif t == "ParamExp" and not any(part.get(k) for k in PARAM_MODIFIERS):
                name = (part.get("Param") or {}).get("Value", "")
                if name == "PWD":
                    out.append(self.cwd)
                elif name in self.vars:
                    out.append(self.vars[name])
                elif name in os.environ:
                    out.append(os.environ[name])
                else:
                    out.append(UNKNOWN)
            else:
                out.append(UNKNOWN)
        return "".join(out)

    def abspath(self, value):
        if value.startswith("~"):
            value = os.path.expanduser(value)
        return os.path.normpath(os.path.join(self.cwd, value))

    def path_hit(self, value):
        """The protected path a word value points at, or None. A value that starts with an unknown
        expansion points nowhere we can tell."""
        if not value or value.startswith(UNKNOWN):
            return None
        path = self.abspath(value).replace(UNKNOWN, "*")
        if any(c in path for c in "*?["):
            return self.project.overlaps(path)
        return self.project.protects(path)

    def unknown_root_names(self, value):
        """For a value like $(git rev-parse --show-toplevel)/paper/source/a.tex: does the known
        part after the last unknown expansion start with a protected project-relative path?"""
        if not value.startswith(UNKNOWN):  # /tmp/s/$d/data/x starts outside the project
            return None
        tail = value.rsplit(UNKNOWN, 1)[1].lstrip("/")
        for p in self.project.paths:
            rel = os.path.relpath(p, self.project.root)
            if not rel.startswith("..") and (tail == rel or tail.startswith(rel + "/")):
                return rel
        return None

    def word_names(self, word, is_program=False):
        """The protected path a word names, or None. A program name or an option word (-x) is
        not taken as a relative path, though a value after '=' (--file=x) is."""
        value = self.literal(word)
        candidates = [] if is_program or value.startswith("-") else [value]
        after = value.split("=", 1)[1] if "=" in value else ""
        if after and not any(c in after for c in "*?[" + UNKNOWN):  # 'file=[^ ]*' is no path
            candidates.append(after)
        if is_program and os.sep in value:
            candidates.append(value)
        for v in candidates:
            hit = self.path_hit(v) or self.unknown_root_names(v)
            if hit:
                return hit
        if params(word) & self.tainted:
            return "a variable set to a protected path"
        return self.project.named_in(self.raw(word), self.cwd)

    def cwd_protected(self):
        return self.project.protects(self.cwd)

    def sub(self, command):
        """Check a nested command string (bash -c, eval, heredoc to a shell)."""
        if self.depth >= MAX_DEPTH:
            raise Blocked("shell commands nested too deeply to check")
        Checker(command, self.cwd, self.project, self.depth + 1, self.tainted, self.vars,
                self.functions).run()

    # walking
    def run(self):
        tree = parse(self.src.decode("utf-8"))
        if tree is None:
            hit = self.project.named_in(self.src.decode("utf-8"), self.cwd) or self.cwd_protected()
            if hit:
                raise Blocked(f"bash-guard could not parse the command, and it names a protected path ({hit})")
            return
        self.stmts(tree.get("Stmts", []))

    def stmts(self, stmts):
        for s in stmts or []:
            self.stmt(s)

    def stmt(self, stmt, involved=False):
        hdoc = ""
        for r in stmt.get("Redirs") or []:
            op = r.get("Op", "")
            word = r.get("Word") or {}
            target = self.literal(word)
            if op in WRITE_REDIRECTS or (op == ">&" and not re.fullmatch(r"\d+|-", target)):
                hit = self.path_hit(target)
                if not hit and params(word) & self.tainted:
                    hit = "a variable set to a protected path"
                if hit:
                    shown = self.raw(word) or target
                    raise Blocked(f"the redirection '{op} {shown}' writes into a protected path ({hit})")
            if r.get("Hdoc"):
                hdoc += self.raw(r["Hdoc"])
            self.nested(word)
        cmd = stmt.get("Cmd")
        if not cmd:
            return
        t = cmd.get("Type")
        if t == "CallExpr":
            self.call(cmd, hdoc, involved)
        elif t == "BinaryCmd" and cmd.get("Op") in ("|", "|&"):
            parts = self.pipeline(cmd)
            inv = involved or any(self.stmt_names(p) for p in parts)
            for p in parts:
                self.stmt(p, inv)
        elif t == "BinaryCmd":
            self.stmt(cmd["X"], involved)
            self.stmt(cmd["Y"], involved)
        elif t == "Subshell":
            saved = self.cwd
            self.stmts(cmd.get("Stmts"))
            self.cwd = saved
        elif t == "ForClause":
            loop = cmd.get("Loop") or {}
            name = (loop.get("Name") or {}).get("Value")
            if name:
                self.vars[name] = UNKNOWN
                if any(self.word_names(w) for w in loop.get("Items") or []):
                    self.tainted.add(name)
            self.nested(loop)
            self.stmts(cmd.get("Do"))
        elif t == "DeclClause":
            for a in cmd.get("Args") or []:
                self.assign(a)
        elif t == "FuncDecl":
            # The body is checked here, where it is defined; calls to the function are then allowed.
            self.functions.add((cmd.get("Name") or {}).get("Value", ""))
            self.nested(cmd.get("Body"), involved)
        else:  # Block, IfClause, WhileClause, CaseClause, TimeClause, TestClause, ...
            self.nested(cmd, involved)

    def pipeline(self, cmd):
        out = []
        for side in (cmd["X"], cmd["Y"]):
            c = side.get("Cmd") or {}
            if c.get("Type") == "BinaryCmd" and c.get("Op") in ("|", "|&") and not side.get("Redirs"):
                out += self.pipeline(c)
            else:
                out.append(side)
        return out

    def stmt_names(self, stmt):
        """Does a statement name a protected path anywhere (words, redirections, heredoc)?"""
        return bool(self.project.named_in(self.raw(stmt), self.cwd)) or any(
            self.word_names(w) for w in self.words_in(stmt))

    def words_in(self, node):
        if isinstance(node, dict):
            if "Parts" in node and "Type" not in node:
                yield node
            for v in node.values():
                yield from self.words_in(v)
        elif isinstance(node, list):
            for v in node:
                yield from self.words_in(v)

    def nested(self, node, involved=False):
        """Check statements nested anywhere in a node: $(..), <(..), if/while/case bodies, ..."""
        if is_stmt(node):
            self.stmt(node, involved)
        elif isinstance(node, dict):
            for v in node.values():
                self.nested(v, involved)
        elif isinstance(node, list):
            for v in node:
                self.nested(v, involved)

    def assign(self, a):
        name = (a.get("Name") or {}).get("Value")
        value = a.get("Value")
        if name and not a.get("Naked"):
            self.vars[name] = self.literal(value) if value else ""
            if a.get("Append") or a.get("Index") or a.get("Array"):
                self.vars[name] = UNKNOWN
            # Tainted only if the value is itself a protected path (x=paper/source/a.tex), not if
            # it is the output of a command that reads one (k=$(grep .. paper/source/a.tex)).
            if value and (self.path_hit(self.vars[name]) or self.unknown_root_names(self.vars[name])):
                self.tainted.add(name)
        if value:
            self.nested(value)

    def call(self, cmd, hdoc, involved):
        for a in cmd.get("Assigns") or []:
            self.assign(a)
        words = cmd.get("Args") or []
        for w in words:
            self.nested(w)
        if not words:
            return
        # Relative paths are resolved against the current folder, so a command working inside a
        # protected folder names it through them; the folder alone does not count.
        named = involved or next((h for h in (self.word_names(w, i == 0) for i, w in enumerate(words))
                                  if h), None)
        if not named and hdoc:
            named = self.project.named_in(hdoc, self.cwd)
        values = []
        for w in words:
            v = self.literal(w)
            # Bash splits an unquoted $var into words: G="git -c x"; $G log runs git.
            if any(p.get("Type") == "ParamExp" for p in w.get("Parts", [])) and len(v.split()) > 1:
                values += v.split()
            else:
                values.append(v)
        self.simple(values, hdoc, named)

    def simple(self, values, hdoc, named):
        """Check one simple command, given as its word values (quotes removed)."""
        al = allowlist()
        prog = os.path.basename(values[0])
        args = values[1:]

        if prog in ("cd", "pushd"):
            dirs = [a for a in args if not a.startswith("-")]
            if dirs and UNKNOWN not in dirs[0] and not any(c in dirs[0] for c in "*?["):
                self.cwd = norm(self.abspath(dirs[0]))
            elif not args:
                self.cwd = os.path.expanduser("~")
            return
        if prog in self.functions:
            return

        wrapper = al["wrappers"].get(prog)
        if wrapper is not None and "start" in wrapper:
            # Embedded commands (find -exec ... ;): check each, keep the rest for the read_only check.
            rest, i = [], 0
            while i < len(args):
                if args[i] in wrapper["start"]:
                    j = i + 1
                    while j < len(args) and args[j] not in wrapper["end"]:
                        j += 1
                    if args[i + 1:j]:
                        self.simple(args[i + 1:j], hdoc, named)
                    i = j + 1
                else:
                    rest.append(args[i])
                    i += 1
            args = rest
        elif wrapper is not None:
            inner = self.unwrap(wrapper, args)
            if inner:
                self.simple(inner, hdoc, named)
            return

        if prog in al["shells"] and "-c" in args:
            i = args.index("-c")
            if i + 1 < len(args):
                self.sub(values[i + 2])
            return
        if prog in al["shells"] and hdoc and not [a for a in args if not a.startswith("-")]:
            self.sub(hdoc)
            return
        if prog == "eval":
            self.sub(" ".join(args))
            return

        if not named:
            return
        if named is True:
            named = "the current folder or a pipeline partner"

        if al["python_names"].match(prog):
            return self.python(values[0], args, named)

        spec = al["read_only"].get(prog)
        if spec is None:
            raise Blocked(f"'{prog}' is not on bash-guard's read-only list, and the command names a "
                          f"protected path ({named})")
        for a in args:
            for rx in spec["except"]:
                if rx.search(a):
                    raise Blocked(f"'{prog}' with '{a}' can write files, and the command names a "
                                  f"protected path ({named})")
        wo = spec["write_operands"]
        if wo:
            # GNU tools accept options anywhere (cp a b -S .bak), so operands are found by skipping
            # options and the values of value_options; every word after "--" is an operand.
            operands, i, value_opts = [], 0, set(spec["value_options"])
            while i < len(args):
                a = args[i]
                if a == "--":
                    operands += args[i + 1:]
                    break
                if a.startswith("-") and a != "-":
                    i += 2 if a in value_opts else 1
                    continue
                operands.append(a)
                i += 1
            if wo == "all":
                picked = operands
            elif wo == "last":
                picked = operands[-1:]
            else:
                picked = [operands[i - 1] for i in wo if i <= len(operands)]
            for a in picked:
                hit = self.path_hit(a)
                if hit:
                    raise Blocked(f"'{prog}' writes its operand '{a}', which is a protected path ({hit})")

    def unwrap(self, spec, args):
        """The words of the command a prefix wrapper runs (empty if none)."""
        value_opts = set(spec.get("value_options", []))
        i = 0
        while i < len(args):
            a = args[i]
            if a == "--":
                i += 1
                break
            if spec.get("assignments") and re.match(r"^[A-Za-z_]\w*=", a):
                i += 1
            elif a.startswith("-") and a != "-":
                i += 2 if a in value_opts else 1
            else:
                break
        return args[i + spec.get("positional", 0):]

    def python(self, prog_word, args, named):
        al = allowlist()
        if UNKNOWN in prog_word:
            raise Blocked(f"cannot tell which Python '{prog_word}' runs, and the command names a "
                          f"protected path ({named})")
        exe = prog_word if os.sep in prog_word else __import__("shutil").which(prog_word)
        exe = python_key(self.abspath(exe)) if exe else None
        if not exe or exe not in guarded_pythons():
            raise Blocked(f"'{prog_word}' does not have bash-guard's runtime hook installed "
                          f"({exe or 'not found'}), and the command names a protected path ({named})")
        i = 0
        while i < len(args):
            a = args[i]
            if a in ("-c", "-m", "-") or not a.startswith("-"):
                break
            for rx in al["python_except"]:
                if rx.search(a):
                    raise Blocked(f"'{prog_word} {a}' skips the site module, so bash-guard's runtime "
                                  f"hook would not load, and the command names a protected path ({named})")
            if a in ("-W", "-X"):
                i += 1
            elif re.match(r"^-[A-Za-z]*[cm]$", a):
                break
            i += 1


def block_message(reason, project):
    """The text Claude sees when bash-guard blocks something."""
    paths = ", ".join(os.path.relpath(p, project.root) for p in project.paths) or "none"
    globs = ", ".join(os.path.relpath(g, project.root) for g in project.globs)
    return (
        f"bash-guard blocked this: {reason}. It is suspected of modifying protected files in this "
        f"project (protected: {paths}{', ' + globs if globs else ''}). If you were trying to modify a "
        f"protected file, do not try to work around the block: protected files may only be changed "
        f"with the Edit or Write tools. This check is overcautious on purpose. If you believe this "
        f"was a false positive that should be allowed, tell the user, so they can add an exception "
        f"(the read-only list is {ALLOWLIST}; protected paths and allowed writer scripts are in "
        f"{project.config_path})."
    )


def check(command, cwd, project):
    """(allowed, reason). project is a Project (or a path to its bash-guard.json)."""
    if not isinstance(project, Project):
        project = Project(project)
    try:
        Checker(command, cwd, project).run()
    except Blocked as b:
        return False, str(b).replace(project.root + os.sep, "")
    except Exception as e:  # a checker bug must not let a write through
        hit = project.named_in(command, norm(cwd)) or project.protects(norm(cwd))
        if hit:
            return False, (f"bash-guard hit an internal error ({type(e).__name__}: {e}), and the "
                           f"command names a protected path ({os.path.relpath(hit, project.root) if os.path.isabs(hit) else hit})")
    return True, ""


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True, help="the project's bash-guard.json")
    ap.add_argument("--cwd", default=os.getcwd())
    ap.add_argument("command", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    cmd = a.command[1:] if a.command[:1] == ["--"] else a.command
    try:
        ok, reason = check(" ".join(cmd), a.cwd, a.config)
    except ConfigError as e:
        print(f"bash-guard: {e}", file=sys.stderr)
        return 2
    print("allow" if ok else f"block: {reason}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""bash-guard runtime hook: guards Python processes started from Claude Code's Bash tool.

A .pth file in the interpreter's site-packages (written by install.py) runs this file at Python
startup when the environment has CLAUDECODE=1, which Claude Code sets for its Bash commands. It adds
an audit hook (PEP 578) that raises PermissionError before:
  - a write to a protected path: open() for writing, os.open with write flags, rename/replace,
    remove, rmdir, truncate, link/symlink targets, chmod/chown/utime, mkdir, shutil copy/move/rmtree
    targets. Reads are never blocked. A project's "writers" (script -> files) may write their files.
  - launching a program whose command line checkperms.py would block (subprocess, os.system,
    os.exec*, os.posix_spawn, os.spawn*, pty.spawn). Launches of bash-guard's own shfmt are skipped.
Protected paths come from every project registered in the state folder (see checkperms.PROJECTS).
Audit hooks catch accidents, not deliberate evasion: C code writing files directly is not seen.
"""


def _bash_guard_install(here):
    import os
    import sys

    def norm(path):  # symlinks resolved; see checkperms.norm
        return os.path.realpath(path)

    busy = [False]
    loaded = {}

    def guard():
        if "checkperms" not in loaded:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "bash_guard_checkperms", os.path.join(here, "checkperms.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            projects = []
            for cfg in mod.registered_projects():
                try:
                    p = mod.Project(cfg)
                except mod.ConfigError:
                    continue
                if p.paths or p.globs:
                    projects.append(p)
            loaded["checkperms"], loaded["projects"] = mod, projects
            main = getattr(sys.modules.get("__main__"), "__file__", None) or (sys.argv[0] if sys.argv else "")
            loaded["script"] = norm(os.path.join(loaded["start_cwd"], main)) if main else ""
        return loaded["checkperms"], loaded["projects"]

    loaded["start_cwd"] = os.getcwd()
    write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
    shfmt_dir = os.path.join(here, "bin") + os.sep
    # audit event -> indexes of its path arguments that are written to
    path_events = {
        "os.rename": (0, 1), "shutil.move": (0, 1), "os.remove": (0,), "os.rmdir": (0,),
        "os.truncate": (0,), "os.link": (1,), "os.symlink": (1,), "os.chmod": (0,), "os.chown": (0,),
        "os.utime": (0,), "os.mkdir": (0,), "os.mkfifo": (0,), "os.mknod": (0,), "os.chflags": (0,),
        "os.setxattr": (0,), "os.removexattr": (0,), "shutil.copyfile": (1,), "shutil.copymode": (1,),
        "shutil.copystat": (1,), "shutil.copytree": (1,), "shutil.rmtree": (0,),
    }
    launch_events = {"subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "pty.spawn"}
    checked_launches = set()

    def deny(mod, project, reason):
        raise PermissionError(mod.block_message(reason, project))

    def check_path(path, what):
        try:
            path = os.fsdecode(path)
        except TypeError:
            return  # a file descriptor
        mod, projects = guard()
        full = norm(path)
        for p in projects:
            hit = p.protects(full)
            if hit and full not in p.writers.get(loaded["script"], ()):
                deny(mod, p, f"{what} '{path}' from a Python process started by a Bash command "
                             f"writes into a protected path ({os.path.relpath(hit, p.root)})")

    def check_launch(event, args):
        import shlex
        cwd = None
        if event == "os.system":
            command = os.fsdecode(args[0])
        else:
            argv = {"subprocess.Popen": 1, "os.exec": 1, "os.posix_spawn": 1, "os.spawn": 2,
                    "pty.spawn": 0}[event]
            argv = args[argv]
            if event == "subprocess.Popen":
                cwd = args[2]
            if isinstance(argv, (str, bytes)):
                argv = [argv]
            argv = [os.fsdecode(a) for a in argv]
            if not argv or os.path.realpath(argv[0]).startswith(shfmt_dir):
                return
            command = shlex.join(argv)
        cwd = os.fsdecode(cwd) if cwd else os.getcwd()
        if (command, cwd) in checked_launches:
            return
        mod, projects = guard()
        for p in projects:
            ok, reason = mod.check(command, cwd, p)
            if not ok:
                deny(mod, p, f"a program launched from Python: {reason}")
        checked_launches.add((command, cwd))

    def hook(event, args):
        if busy[0]:
            return
        if event == "open":
            path, mode, flags = args
            if path is None or isinstance(path, int):
                return
            if not ((mode and any(c in mode for c in "wax+")) or (flags and flags & write_flags)):
                return
            what = "opening"
        elif event in path_events:
            what = event
        elif event in launch_events:
            busy[0] = True
            try:
                check_launch(event, args)
            finally:
                busy[0] = False
            return
        else:
            return
        busy[0] = True
        try:
            if event == "open":
                check_path(path, f"open(mode={mode!r})" if mode else "os.open")
            else:
                for i in path_events[event]:
                    if i < len(args) and args[i] is not None:
                        check_path(args[i], what)
        finally:
            busy[0] = False

    sys.addaudithook(hook)
    sys.modules["_bash_guard_active"] = type(sys)("_bash_guard_active")  # lets install.py verify


try:
    _bash_guard_install(__import__("os").path.dirname(__file__))
except Exception as _e:  # a broken guard must not break every Python run
    __import__("sys").stderr.write(f"bash-guard runtime.py failed to load: {_e!r}\n")

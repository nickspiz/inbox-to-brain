#!/usr/bin/env python3
"""Rebuild docs/demo.gif by running the real scripts in a temp folder.

  python3 docs/render_demo.py        (needs Pillow: pip install pillow)

docs/demo.tape is the same demo for charmbracelet/vhs.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import termgif as t  # noqa: E402


def colour(line):
    s = line.lstrip()
    if s.startswith(("would move", "moved")):
        return [(line, t.GREEN)]
    if s.startswith("stays"):
        return [(line, t.YELLOW)]
    return [(line, t.FG)]


def main():
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "demo"
        work.mkdir()
        shutil.copytree(ROOT / "starter-vault", work / "my-vault")
        for f in (ROOT / "examples" / "sample-inbox").glob("*.md"):
            shutil.copy(f, work / "my-vault" / "00_Inbox" / f.name)
        for f in ("router.py", "validator.py", "notes.py"):
            shutil.copy(ROOT / f, work / f)
        env = {"PATH": os.environ["PATH"], "HOME": tmp}

        def sh(cmd):
            r = subprocess.run(cmd, shell=True, cwd=work, env=env, capture_output=True, text=True)
            return [ln for ln in (r.stdout + r.stderr).rstrip("\n").split("\n")]

        cmds = [
            "ls my-vault/00_Inbox",
            "python3 router.py --vault my-vault",
            "python3 router.py --vault my-vault --apply",
            "cd my-vault && find Projects Knowledge 00_Inbox -name '*.md' | sort",
        ]
        steps = []
        for i, cmd in enumerate(cmds):
            out = sh(cmd)
            steps.append(("type", cmd))
            steps.append(("outc", [colour(ln) for ln in out]))
            steps.append(("pause", 1.8 if i != 1 else 2.6))
            if i < len(cmds) - 1:
                steps.append(("clear",))
    term = t.Term(cols=100, rows=19, size=15, title="demo: inbox-to-brain")
    term.run(steps, type_chunk=3, type_dt=0.04, line_dt=0.14)
    term.save(HERE / "demo.gif")


if __name__ == "__main__":
    main()

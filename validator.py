#!/usr/bin/env python3
"""validator.py: find inbox notes that are not worth keeping as they are.

Flags, per note:
  too-short        less than min_chars of text after the frontmatter
  no-frontmatter   no --- block at the top
  todo-only        nothing but checkbox lines
  name-collision   the same file name already exists in Projects/ or Knowledge/

The report goes to <inbox>/_NEEDS_REVIEW.md. This script never moves, edits
or deletes a note. It only rewrites its own report.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import notes

TODO_LINE = re.compile(r"^\s*[-*]\s\[[ xX]\]\s")


def existing_names(vault: Path, cfg: dict) -> set[str]:
    names: set[str] = set()
    for key in ("projects", "knowledge"):
        root = vault / cfg["folders"][key]
        if root.is_dir():
            names.update(p.stem.lower() for p in root.rglob("*.md"))
    return names


def check(path: Path, cfg: dict, taken: set[str]) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = notes.parse_note(text)
    problems: list[tuple[str, str]] = []

    chars = len(body.strip())
    if chars < cfg["min_chars"]:
        problems.append(("too-short", f"{chars} characters, the minimum is {cfg['min_chars']}"))
    if fm is None:
        problems.append(("no-frontmatter", "the note starts without a --- block"))
    lines = [ln for ln in body.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    todos = sum(1 for ln in lines if TODO_LINE.match(ln))
    if todos and todos == len(lines):
        problems.append(("todo-only", f"{todos} checkbox lines and no prose"))
    if path.stem.lower() in taken:
        problems.append(("name-collision", "a note with this file name already exists outside the inbox"))
    return problems


def build_report(rows: list[tuple[Path, list[tuple[str, str]]]], total: int) -> str:
    stamp = time.strftime("%Y-%m-%d %H:%M")
    out = [
        "# Needs review",
        "",
        f"Checked {total} inbox note(s) on {stamp}. Nothing was moved or deleted.",
        "",
    ]
    if not rows:
        out.append("Everything looks fine.")
        return "\n".join(out) + "\n"
    out += ["| Note | Flag | Why |", "|---|---|---|"]
    for path, problems in rows:
        for flag, why in problems:
            out.append(f"| [[{path.stem}]] | {flag} | {why} |")
    out += ["", "Fix the note, rename it, or delete it yourself, then run the validator again.", ""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Report inbox notes that need a human look. Never moves files.")
    ap.add_argument("--vault", default=None, help="vault root (default: $INBOX_VAULT or the current folder)")
    ap.add_argument("--config", default=None)
    ap.add_argument("--print", dest="print_only", action="store_true", help="print the report, do not write the file")
    args = ap.parse_args(argv)

    vault = Path(args.vault).expanduser().resolve() if args.vault else notes.default_vault()
    cfg = notes.load_config(vault, args.config)
    inbox = vault / cfg["folders"]["inbox"]
    if not inbox.is_dir():
        print(f"No inbox folder at {inbox}", file=sys.stderr)
        return 1

    files = notes.inbox_notes(vault, cfg)
    taken = existing_names(vault, cfg)
    rows = [(f, p) for f in files if (p := check(f, cfg, taken))]
    report = build_report(rows, len(files))
    if args.print_only:
        print(report)
    else:
        (inbox / "_NEEDS_REVIEW.md").write_text(report, encoding="utf-8")
        print(f"Checked {len(files)} note(s), {len(rows)} need review. Report: {inbox / '_NEEDS_REVIEW.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

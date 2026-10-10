#!/usr/bin/env python3
"""router.py: file notes from the inbox into the right folder.

A note moves when its frontmatter says what it is:

  type: decision                  -> Projects/<slug>/decisions/
  type: insight | knowledge       -> Projects/<slug>/knowledge/
  (no known project, but a tag)   -> Knowledge/<tag>/

The project comes from `project: <slug>` or a `project/<slug>` tag, and must
be listed in inbox-to-brain.toml. Anything unclear stays in the inbox and is
listed with the reason.

It only prints what it would do, unless you pass --apply.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

import notes


def plan(vault: Path, cfg: dict) -> list[dict]:
    """Decide what to do with every inbox note. Touches nothing."""
    folders = cfg["folders"]
    actions = []
    for path in notes.inbox_notes(vault, cfg):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, _ = notes.parse_note(text)
        act = {"file": path, "dest": None, "project": None, "reason": ""}
        if fm is None:
            act["reason"] = "no frontmatter, so I cannot tell what this is"
        else:
            kind = notes.note_type(fm)
            raw = notes.raw_project(fm)
            slug = notes.resolve_project(raw, cfg)
            if kind is None:
                act["reason"] = "no type (decision, insight or knowledge)"
            elif raw and not slug:
                act["reason"] = f"project '{raw}' is not in the config"
            elif slug:
                sub = "decisions" if kind == "decision" else "knowledge"
                act["dest"] = vault / folders["projects"] / slug / sub / path.name
                act["project"] = slug
            else:
                group = notes.knowledge_group(fm, cfg)
                act["dest"] = vault / folders["knowledge"] / group / path.name
        if act["dest"] is not None and act["dest"].exists():
            act["reason"] = "a note with this name is already there"
            act["dest"] = None
        actions.append(act)
    return actions


def add_to_index(vault: Path, cfg: dict, act: dict) -> None:
    """Link the moved note from the project's index page, if there is one."""
    slug = act["project"]
    if not slug:
        return
    index = vault / cfg["folders"]["projects"] / slug / f"{slug}.md"
    if not index.is_file():
        return
    heading = "## Decisions" if act["dest"].parent.name == "decisions" else "## Knowledge"
    link = f"- [[{act['dest'].stem}]]"
    text = index.read_text(encoding="utf-8")
    if link in text:
        return
    if re.search(rf"^{re.escape(heading)}\s*$", text, re.M):
        text = re.sub(rf"^({re.escape(heading)}\s*\n)", rf"\1{link}\n", text, count=1, flags=re.M)
    else:
        text = text.rstrip("\n") + f"\n\n{heading}\n{link}\n"
    index.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Route inbox notes by frontmatter. Dry run unless --apply.")
    ap.add_argument("--vault", default=None, help="vault root (default: $INBOX_VAULT or the current folder)")
    ap.add_argument("--config", default=None, help="path to inbox-to-brain.toml or .json")
    ap.add_argument("--apply", action="store_true", help="actually move the files")
    args = ap.parse_args(argv)

    vault = Path(args.vault).expanduser().resolve() if args.vault else notes.default_vault()
    cfg = notes.load_config(vault, args.config)
    if not (vault / cfg["folders"]["inbox"]).is_dir():
        print(f"No inbox folder at {vault / cfg['folders']['inbox']}", file=sys.stderr)
        return 1

    actions = plan(vault, cfg)
    moved = kept = 0
    for act in actions:
        name = act["file"].name
        if act["dest"] is None:
            kept += 1
            print(f"  stays   {name}  ({act['reason']})")
            continue
        rel = act["dest"].relative_to(vault)
        if args.apply:
            act["dest"].parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(act["file"]), str(act["dest"]))
            add_to_index(vault, cfg, act)
            print(f"  moved   {name}  ->  {rel}")
        else:
            print(f"  would move  {name}  ->  {rel}")
        moved += 1

    verb = "moved" if args.apply else "would move"
    print(f"\n{verb} {moved}, staying in the inbox {kept}." + ("" if args.apply else "  Dry run. Add --apply to do it."))
    return 0


if __name__ == "__main__":
    sys.exit(main())

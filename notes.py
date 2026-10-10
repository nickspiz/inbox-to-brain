"""Shared helpers for router.py and validator.py. Standard library only."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

try:  # Python 3.11+
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None

CONFIG_NAMES = ("inbox-to-brain.toml", "inbox-to-brain.json")
NOTE_TYPES = ("decision", "insight", "knowledge")
# Tags that describe the kind of note, so they never name a Knowledge folder.
META_TAGS = {"insight", "decision", "knowledge", "inbox", "todo", "draft", "wip", "note", "tag"}

DEFAULTS = {
    "projects": [],
    "aliases": {},
    "min_chars": 200,
    "folders": {"inbox": "00_Inbox", "projects": "Projects", "knowledge": "Knowledge"},
    "fallback_group": "_general",
}

FRONTMATTER_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.DOTALL)


# ---------------------------------------------------------------- config

def load_config(vault: Path, explicit: str | None = None) -> dict:
    path = Path(explicit) if explicit else next(
        (vault / n for n in CONFIG_NAMES if (vault / n).is_file()), None)
    cfg = json.loads(json.dumps(DEFAULTS))  # deep copy
    if path is None:
        return cfg
    if path.suffix == ".toml":
        if tomllib is None:
            raise SystemExit(f"{path} needs Python 3.11+. Use inbox-to-brain.json instead.")
        with path.open("rb") as fh:
            user = tomllib.load(fh)
    else:
        user = json.loads(path.read_text(encoding="utf-8"))
    for key, val in user.items():
        if isinstance(val, dict) and isinstance(cfg.get(key), dict):
            cfg[key].update(val)
        else:
            cfg[key] = val
    return cfg


def default_vault() -> Path:
    return Path(os.environ.get("INBOX_VAULT") or os.getcwd()).expanduser().resolve()


# ---------------------------------------------------------------- notes

def _unquote(s: str) -> str:
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        return s[1:-1]
    return s


def parse_note(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter, body). Frontmatter is None when there is no block.

    Understands `key: value`, `key: [a, b]` and block lists (`- a`).
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    fm: dict = {}
    lines = m.group(1).split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#") or line[:1].isspace() or ":" not in line:
            i += 1
            continue
        key, _, val = line.partition(":")
        key, val = key.strip().lower(), val.strip()
        if val == "":
            items, j = [], i + 1
            while j < len(lines) and lines[j].lstrip().startswith("-"):
                items.append(_unquote(lines[j].lstrip()[1:].strip()))
                j += 1
            fm[key] = [x for x in items if x] if items else ""
            i = j
            continue
        if val.startswith("[") and val.endswith("]"):
            fm[key] = [_unquote(x.strip()) for x in val[1:-1].split(",") if x.strip()]
        else:
            fm[key] = _unquote(val)
        i += 1
    return fm, text[m.end():]


def tag_list(fm: dict) -> list[str]:
    raw = fm.get("tags", [])
    if isinstance(raw, str):
        raw = [t for t in re.split(r"[,\s]+", raw) if t]
    return [str(t).strip().lstrip("#").lower() for t in raw if str(t).strip()]


def note_type(fm: dict) -> str | None:
    raw = fm.get("type", "")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""
    raw = str(raw).strip().lower()
    if raw in NOTE_TYPES:
        return raw
    for t in tag_list(fm):
        if t in NOTE_TYPES:
            return t
    return None


def raw_project(fm: dict) -> str | None:
    """The project named by the `project:` field or a `project/<slug>` tag."""
    value = fm.get("project", "")
    if isinstance(value, list):
        value = value[0] if value else ""
    value = str(value).strip()
    if value and value.lower() not in {"null", "none", "n/a", "-", "<slug>"}:
        return value.split(",")[0].strip()
    for t in tag_list(fm):
        if t.startswith("project/") and len(t) > len("project/"):
            return t[len("project/"):]
    return None


def resolve_project(raw: str | None, cfg: dict) -> str | None:
    """Map a raw name to a configured project slug, or None."""
    if not raw:
        return None
    wanted = raw.strip().lower()
    wanted = {k.lower(): v for k, v in cfg["aliases"].items()}.get(wanted, wanted)
    for slug in cfg["projects"]:
        if slug.lower() == wanted.lower():
            return slug
    return None


def knowledge_group(fm: dict, cfg: dict) -> str:
    for t in tag_list(fm):
        if t in META_TAGS or t.startswith("project/") or "/" in t:
            continue
        clean = re.sub(r"[^a-z0-9_-]+", "-", t).strip("-")
        if clean:
            return clean
    return cfg["fallback_group"]


def inbox_notes(vault: Path, cfg: dict) -> list[Path]:
    inbox = vault / cfg["folders"]["inbox"]
    if not inbox.is_dir():
        return []
    return sorted(p for p in inbox.glob("*.md") if not p.name.startswith("_") and p.name.lower() != "readme.md")

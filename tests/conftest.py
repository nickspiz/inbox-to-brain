import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

LONG = "This note has enough text to pass the length check. " * 6


@pytest.fixture()
def vault(tmp_path):
    """A temporary copy of the starter vault."""
    dest = tmp_path / "vault"
    shutil.copytree(ROOT / "starter-vault", dest)
    return dest


def write_note(vault, name, fm=None, body=LONG):
    text = body if fm is None else f"---\n{fm}\n---\n\n{body}\n"
    path = vault / "00_Inbox" / name
    path.write_text(text, encoding="utf-8")
    return path

import validator
from conftest import LONG, write_note


def report(vault, *flags):
    assert validator.main(["--vault", str(vault), *flags]) == 0
    return (vault / "00_Inbox" / "_NEEDS_REVIEW.md").read_text()


def test_clean_inbox(vault):
    write_note(vault, "ok.md", "type: insight\nproject: example-app")
    assert "Everything looks fine" in report(vault)


def test_too_short(vault):
    write_note(vault, "short.md", "type: insight", body="tiny")
    text = report(vault)
    assert "[[short]]" in text and "too-short" in text


def test_missing_frontmatter(vault):
    write_note(vault, "bare.md")
    assert "no-frontmatter" in report(vault)


def test_todo_only(vault):
    write_note(vault, "todo.md", "type: insight", body="# Today\n- [ ] one\n- [x] two\n" + "- [ ] more\n" * 40)
    assert "todo-only" in report(vault)


def test_todo_with_prose_is_fine(vault):
    write_note(vault, "mixed.md", "type: insight", body=LONG + "\n- [ ] follow up")
    assert "todo-only" not in report(vault)


def test_name_collision_with_project_and_knowledge(vault):
    (vault / "Projects/example-app/decisions/dup.md").write_text("x")
    (vault / "Knowledge/misc").mkdir()
    (vault / "Knowledge/misc/Other.md").write_text("x")
    write_note(vault, "dup.md", "type: decision")
    write_note(vault, "other.md", "type: decision")
    text = report(vault)
    assert "[[dup]]" in text and "[[other]]" in text and text.count("name-collision") == 2


def test_never_moves_or_edits_notes(vault):
    note = write_note(vault, "keep.md")
    before = note.read_text()
    report(vault)
    assert note.exists() and note.read_text() == before
    assert sorted(p.name for p in (vault / "00_Inbox").glob("*.md")) == ["_NEEDS_REVIEW.md", "keep.md"]


def test_report_is_not_checked_as_a_note(vault):
    report(vault)
    assert "_NEEDS_REVIEW" not in report(vault)


def test_min_chars_from_config(vault):
    (vault / "inbox-to-brain.toml").write_text("min_chars = 5\n")
    write_note(vault, "tiny.md", "type: insight", body="long enough now")
    assert "too-short" not in report(vault)


def test_print_flag_writes_nothing(vault, capsys):
    write_note(vault, "bare.md")
    validator.main(["--vault", str(vault), "--print"])
    assert "no-frontmatter" in capsys.readouterr().out
    assert not (vault / "00_Inbox/_NEEDS_REVIEW.md").exists()


def test_missing_inbox(tmp_path):
    assert validator.main(["--vault", str(tmp_path)]) == 1

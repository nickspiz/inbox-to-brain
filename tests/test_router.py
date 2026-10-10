import json

import notes
import router
from conftest import ROOT, write_note


def run(vault, *flags):
    return router.main(["--vault", str(vault), *flags])


def test_dry_run_moves_nothing(vault, capsys):
    note = write_note(vault, "a.md", "type: decision\nproject: example-app")
    assert run(vault) == 0
    assert note.exists()
    out = capsys.readouterr().out
    assert "would move" in out and "Dry run" in out
    assert not (vault / "Projects/example-app/decisions/a.md").exists()


def test_decision_goes_to_project_decisions(vault):
    write_note(vault, "a.md", "type: decision\nproject: example-app")
    run(vault, "--apply")
    assert (vault / "Projects/example-app/decisions/a.md").is_file()
    assert not (vault / "00_Inbox/a.md").exists()


def test_insight_and_knowledge_go_to_project_knowledge(vault):
    write_note(vault, "i.md", "type: insight\nproject: example-app")
    write_note(vault, "k.md", "type: knowledge\ntags: [knowledge, project/example-app]")
    run(vault, "--apply")
    assert (vault / "Projects/example-app/knowledge/i.md").is_file()
    assert (vault / "Projects/example-app/knowledge/k.md").is_file()


def test_project_tag_alone_is_enough(vault):
    write_note(vault, "t.md", "tags: [decision, project/example-app]")
    run(vault, "--apply")
    assert (vault / "Projects/example-app/decisions/t.md").is_file()


def test_alias_resolves(vault):
    write_note(vault, "al.md", "type: insight\nproject: app")
    run(vault, "--apply")
    assert (vault / "Projects/example-app/knowledge/al.md").is_file()


def test_no_project_goes_to_knowledge_group(vault):
    write_note(vault, "g.md", "type: knowledge\ntags: [knowledge, Databases]")
    run(vault, "--apply")
    assert (vault / "Knowledge/databases/g.md").is_file()


def test_no_group_tag_uses_fallback(vault):
    write_note(vault, "f.md", "type: insight\ntags: [insight]")
    run(vault, "--apply")
    assert (vault / "Knowledge/_general/f.md").is_file()


def test_unknown_project_stays_and_says_why(vault, capsys):
    note = write_note(vault, "u.md", "type: insight\nproject: billing-v2")
    run(vault, "--apply")
    assert note.exists()
    assert "billing-v2" in capsys.readouterr().out


def test_no_frontmatter_stays(vault):
    note = write_note(vault, "n.md")
    run(vault, "--apply")
    assert note.exists()


def test_missing_type_stays(vault):
    note = write_note(vault, "m.md", "project: example-app")
    run(vault, "--apply")
    assert note.exists()


def test_never_overwrites(vault, capsys):
    dest = vault / "Projects/example-app/decisions"
    (dest / "same.md").write_text("original")
    note = write_note(vault, "same.md", "type: decision\nproject: example-app")
    run(vault, "--apply")
    assert note.exists() and (dest / "same.md").read_text() == "original"
    assert "already there" in capsys.readouterr().out


def test_underscore_and_readme_files_are_ignored(vault):
    write_note(vault, "_NEEDS_REVIEW.md", "type: decision\nproject: example-app")
    write_note(vault, "README.md", "type: decision\nproject: example-app")
    run(vault, "--apply")
    assert (vault / "00_Inbox/_NEEDS_REVIEW.md").exists() and (vault / "00_Inbox/README.md").exists()


def test_index_page_gets_a_link(vault):
    write_note(vault, "linked.md", "type: decision\nproject: example-app")
    run(vault, "--apply")
    run(vault, "--apply")  # second run must not duplicate anything
    index = (vault / "Projects/example-app/example-app.md").read_text()
    assert index.count("[[linked]]") == 1
    assert index.index("## Decisions") < index.index("[[linked]]") < index.index("## Knowledge")


def test_projects_come_from_config_only(vault):
    (vault / "inbox-to-brain.toml").write_text('projects = ["other"]\n')
    note = write_note(vault, "x.md", "type: decision\nproject: example-app")
    run(vault, "--apply")
    assert note.exists()  # example-app is no longer a known project


def test_json_config(vault):
    (vault / "inbox-to-brain.toml").unlink()
    (vault / "inbox-to-brain.json").write_text(json.dumps({"projects": ["shop"]}))
    write_note(vault, "s.md", "type: decision\nproject: shop")
    run(vault, "--apply")
    assert (vault / "Projects/shop/decisions/s.md").is_file()


def test_custom_folder_names(vault):
    (vault / "inbox-to-brain.toml").write_text(
        'projects = ["example-app"]\n[folders]\ninbox = "Inbox"\nprojects = "Work"\nknowledge = "Wiki"\n')
    (vault / "00_Inbox").rename(vault / "Inbox")
    (vault / "Inbox" / "d.md").write_text("---\ntype: decision\nproject: example-app\n---\nbody")
    run(vault, "--apply")
    assert (vault / "Work/example-app/decisions/d.md").is_file()


def test_missing_inbox_is_an_error(tmp_path):
    assert router.main(["--vault", str(tmp_path)]) == 1


def test_parse_variants():
    fm, body = notes.parse_note("---\ntype: 'insight'\ntags:\n  - a\n  - project/x\nproject: x, y\n---\nhello")
    assert fm["type"] == "insight" and fm["tags"] == ["a", "project/x"] and body == "hello"
    assert notes.raw_project(fm) == "x"
    assert notes.parse_note("no block here")[0] is None


def test_sample_inbox_end_to_end(vault, capsys):
    for sample in (ROOT / "examples/sample-inbox").glob("*.md"):
        (vault / "00_Inbox" / sample.name).write_text(sample.read_text())
    run(vault, "--apply")
    assert (vault / "Projects/example-app/decisions/2026-10-01-0930-retry-with-backoff.md").is_file()
    assert (vault / "Projects/example-app/knowledge/2026-10-02-1415-ios-simulator-clock.md").is_file()
    assert (vault / "Knowledge/databases/2026-10-03-1100-postgres-vacuum.md").is_file()
    left = sorted(p.name for p in (vault / "00_Inbox").glob("*.md"))
    assert left == ["2026-10-03-1630-todo.md", "2026-10-04-0900-quick-thought.md", "2026-10-04-1000-mystery-project.md"]

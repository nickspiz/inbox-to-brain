---
description: Flag inbox notes that are too short, have no frontmatter, are only a todo list, or clash by name
allowed-tools: Bash
---

Check the inbox and report. This command never moves or deletes anything.

```bash
python3 validator.py --vault .
```

Then read `00_Inbox/_NEEDS_REVIEW.md` and show the user the table.

Flags: `too-short`, `no-frontmatter`, `todo-only`, `name-collision`.

For each flagged note, suggest one of: expand it, rename it, or delete it. Let the user decide. Do not edit or delete the notes yourself unless asked.

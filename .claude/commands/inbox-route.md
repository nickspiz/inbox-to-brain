---
description: Route inbox notes into Projects/<slug>/ or Knowledge/<group>/ by their frontmatter
allowed-tools: Bash
---

Show what the inbox router would do, then do it only if the user agrees.

1. Preview. Nothing moves:

```bash
python3 router.py --vault .
```

2. Show the user the list: which notes would move and where, and which stay with the reason.
3. If the user says yes, run it for real:

```bash
python3 router.py --vault . --apply
```

4. Report the final counts. For notes that stayed, say what to fix (add a `type:`, add the project to `inbox-to-brain.toml`, rename a clashing file).

If the scripts live somewhere else, change the path. Never move notes by hand to get around a "stays" reason.

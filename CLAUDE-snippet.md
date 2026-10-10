## Notes: after a non-trivial task, write to the inbox

When you finish something that taught you a pattern, a gotcha or a decision worth keeping, write a short note into `00_Inbox/`. Skip typo fixes and plain bug fixes.

- File name: `YYYY-MM-DD-HHMM-short-slug.md`
- 3 to 10 lines of body: what happened, why it matters, how to reuse it
- Start from `_templates/` (decision, insight, knowledge) and keep the frontmatter:

```markdown
---
type: insight            # decision | insight | knowledge
project: my-project      # must be listed in inbox-to-brain.toml, or leave out
tags: [insight, project/my-project]
---

# One-line title

Body, 3 to 10 lines.
```

- Search for an existing note on the same topic first. If there is one, extend it instead of adding a new file.
- Never put secrets, tokens or personal data in a note.
- Do not file notes yourself. Run `/inbox-route` when asked, and `/validate-inbox` to see what needs cleaning up.

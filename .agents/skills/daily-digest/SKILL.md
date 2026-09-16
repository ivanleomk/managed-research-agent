---
name: daily-digest
description: Use when producing a recurring daily research update (email/Telegram-ready). Fixed template, short, actionable.
---

# Daily research digest

## Input
Expect a standing brief like: topics, tickers, repos, or queries to watch.

## Steps
1. Re-run `openalex-lit-review` and/or `edgar-filings` and/or `web-source-triage` for *new since yesterday* only.
2. If nothing new: write a 3-line "no material updates" digest — still deliver.
3. Write `out/digest-YYYY-MM-DD.md`:

```markdown
# Daily research · YYYY-MM-DD

## What moved
- ...

## Worth reading
1. ...

## Watch next
- ...

## Sources
- ...
```

4. Keep under ~400 words. Subject line suggestion on the first line as HTML comment: `<!-- subject: ... -->`

## Scheduling note (for operators)
Invoke this skill via Managed Agents / CLI on a cron; deliver `out/digest-*.md` by email or chat. The skill itself only produces the file.

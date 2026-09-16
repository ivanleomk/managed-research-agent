---
name: openalex-lit-review
description: Use when researching academic papers, citations, authors, or ML/AI literature. Queries the OpenAlex API (no key required for light use) and returns a structured reading list.
---

# OpenAlex literature review

## API
Base: `https://api.openalex.org`
Mailto courtesy: always pass `mailto=ivanleomk@gmail.com` (or the operator's email) as a query param.

## Common calls
```bash
# Search works
curl -sG "https://api.openalex.org/works" \
  --data-urlencode "search=LLM as a judge evaluation" \
  --data-urlencode "filter=from_publication_date:2024-01-01" \
  --data-urlencode "sort=cited_by_count:desc" \
  --data-urlencode "per-page=10" \
  --data-urlencode "mailto=ivanleomk@gmail.com"

# Get one work by OpenAlex ID
curl -sG "https://api.openalex.org/works/W2741809807" \
  --data-urlencode "mailto=ivanleomk@gmail.com"
```

## Output
Write `out/raw/openalex-<slug>.json` and a table in the brief:

| Year | Title | Authors (first) | Cited | URL |
|------|-------|-----------------|-------|-----|

Include abstract/TLDR in 1–2 sentences per paper when available (`abstract_inverted_index` may need reconstruction — if painful, skip abstract and use title + topics).

## Tips
- Filter by concept IDs when search is noisy.
- Prefer works with `primary_location.landing_page_url` or `doi`.
- Cap at 10 papers unless asked for more.

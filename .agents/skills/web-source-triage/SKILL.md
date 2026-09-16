---
name: web-source-triage
description: Use when you need product docs, blogs, or IR pages. Prefer curl + url fetch; identify canonical sources; avoid unbounded crawling.
---

# Web source triage

## When to use
After APIs, or when the answer lives on docs/IR pages.

## Method
1. Start from known seeds (docs URLs, GitHub README, company IR).
2. `curl -sL -A "ResearchAgent/0.1" <url>` — save HTML/text under `out/raw/web/`.
3. Extract: title, publish date if present, 5–10 key claims.
4. Rank sources: primary docs > official blog > third-party.

## Do not
- Crawl entire sites or follow infinite pagination.
- Log into anything or bypass paywalls.
- Treat SEO listicles as primary evidence.

## Output
For each kept page: URL, why trusted, 3 bullets of substance.

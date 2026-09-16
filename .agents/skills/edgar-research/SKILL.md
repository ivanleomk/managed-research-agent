---
name: edgar-research
description: When researching US public companies, pull 10-K and 10-Q filings from SEC EDGAR.
---

# Financial research — use EDGAR

When doing financial research on a US public company, use **SEC EDGAR** (`data.sec.gov`) — not random web pages.

## What to fetch

| Filing | Use for |
|--------|---------|
| **10-K** | Annual report — business, risks, full-year financials |
| **10-Q** | Quarterly report — interim financials and updates |

## Workflow

1. **Ticker → CIK** — company tickers JSON:
   ```bash
   curl -s -A "ResearchAgent/0.1 (demo@example.com)" \
     "https://www.sec.gov/files/company_tickers.json"
   ```
   CIK is zero-padded to 10 digits.

2. **List filings** — submissions JSON:
   ```bash
   curl -s -A "ResearchAgent/0.1 (demo@example.com)" \
     "https://data.sec.gov/submissions/CIK0001045810.json"
   ```
   Read `filings.recent` for `form`, `filingDate`, `accessionNumber`, `primaryDocument`.

3. **Open a filing** when you need quotes:
   `https://www.sec.gov/Archives/edgar/data/{cik}/{accession-no-dashes}/{primaryDocument}`

## Rules

- Set a descriptive User-Agent on every SEC request.
- Cite filing form, date, and URL.
- Do not invent financial numbers.

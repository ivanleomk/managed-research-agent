# managed-research-agent

Skills for an Antigravity → Managed Agents research workflow.

**Story:** tune skills locally (Antigravity) → invoke via CLI → ship as a Managed Agent that can run a **daily research digest**.

## Layout

```
.agents/
  AGENTS.md
  skills/
    research-brief/SKILL.md      # orchestrator
    openalex-lit-review/SKILL.md # papers (no key)
    edgar-filings/SKILL.md       # SEC filings
    web-source-triage/SKILL.md   # careful curl/docs
    daily-digest/SKILL.md        # recurring brief template
```

## Local (Antigravity)
Point the agent at this repo / mount `.agents`. Try:

> Use research-brief: what are the best 2025–2026 papers on LLM-as-a-judge for agent evals? Cite OpenAlex.

## Managed Agents
Mount this repo (or the `.agents` folder) as an environment source so skills auto-discover under `.agents/skills/*/SKILL.md`. Same prompt online.

## Daily agent
Cron a Managed Agent / CLI job with:

> Run daily-digest for topics: managed agents, LLM-as-judge, tool-use evals. Prefer OpenAlex + primary docs.

Deliver `out/digest-YYYY-MM-DD.md` however you like (email, Telegram, Drive).

## SVHN note
CNN/SVHN demos stay in Antigravity local talks — this repo is the **research** track for Managed Agents productization.


## Talk snippets (Interactions ladder)

See `talk/TALK.md` and `talk/snippets/01_*.py` … `06_*.py`.

Progression for slides: hello → sync tools → **background async** → background+tools → managed agent → **EDGAR research agent**.

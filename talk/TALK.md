# Builders Night — Interactions → Antigravity → Managed Agents

## Three acts (30 min + Q&A)

### Act 1 — Tour of the Interactions API
Goal: show why complex apps stay small on Interactions vs rolling your own agent loop.

| Beat | Snippet | Feature |
|------|---------|---------|
| Hello | `01_hello_interaction.py` | One call, typed `steps`, `output_text` |
| Tools | `02_sync_function_calling.py` | Function declarations + `previous_interaction_id` (server state) |
| Background | `03_background_async.py` | `background=True` — no 60s HTTP death |
| Background + tools | `04_background_tools_loop.py` | Poll `requires_action` → submit `function_result` |

**Line to land:** generateContent makes you own history, timeouts, and the tool loop. Interactions gives you state, background, and observable steps.

### Act 2 — Antigravity (tune here)
Goal: prototype the research agent locally. All skill work happens in this act.

- Open Antigravity with this repo (`.agents/AGENTS.md` + skills).
- Live-tune **EDGAR** skill: ticker → CIK → filings → brief.
- Optional small stitch: `design-md` skill for one-pagers.
- Optional speed demo: SVHN skill (~30s train on Mac) if you want “agents write code” energy.
- Same harness via CLI once the skill feels right.

**Line to land:** skills are just markdown + optional scripts. You iterate locally until the agent does the research loop you want.

### Act 3 — Managed Agents (ship the tuned thing)
Goal: combine Act 1 surface + Act 2 skills. No re-tuning — mount and launch.

- Snippet `05_managed_agent_remote.py` — `agent=` + `environment="remote"` + `background=True`.
- Snippet `06_edgar_research_agent.py` — same EDGAR / research-brief skills, now online (repo mounted as a `repository` source).
- CLI beat: `gemini-api agents init` → paste skills into the scaffold → `agents test` → `agents create` → `run --agent edgar-research-agent`. Same `.agents` conventions, zero Python. See `talk/GEMINI_API_CLI.md` + `talk/cli-agent/`.
- Punchline: local skill → Managed Agent daily digest / scheduled run.

**Line to land:** Interactions is how you call it; Antigravity is how you shape it; Managed Agents is how you run it hosted — and the CLI is how you ship it from a terminal.

## What we do NOT cover tonight
- Harbor / Kaggle evals (park for a longer session)
- Deep OpenAlex (optional Q&A depth)

## Repo map for demos
- Skills: `.agents/skills/edgar-filings`, `research-brief`, `design-md`, …
- Snippets: `talk/snippets/01_*.py` … `06_*.py`
- CLI agent scaffold: `talk/cli-agent/` (walkthrough: `talk/GEMINI_API_CLI.md`)
- Validation results + API traces: `talk/SNIPPET_RESULTS.md`, `talk/logs/`
- GitHub: `ivanleomk/managed-research-agent`

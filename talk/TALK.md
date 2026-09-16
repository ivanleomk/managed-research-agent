# Builders Night — Interactions → Antigravity → Managed Agents

## Arc (30 min + Q&A)
1. **Interactions** — tools get easier as apps get harder (snippets 01→04)
2. **Antigravity local** — SVHN skill (~30s train) + iterate
3. **CLI** — same harness, scriptable
4. **Managed Agents** — mount skills, bring online
5. **Custom research agent** — EDGAR skill → daily digest

## Snippet ladder (present these)
| # | File | Point |
|---|------|-------|
| 01 | `01_hello_interaction.py` | One call, typed steps |
| 02 | `02_sync_function_calling.py` | Custom tools + `previous_interaction_id` |
| 03 | `03_background_async.py` | `background=True` — live/long jobs without HTTP timeouts |
| 04 | `04_background_tools_loop.py` | Background + tools → poll `requires_action` → result |
| 05 | `05_managed_agent_remote.py` | `agent=` + `environment="remote"` |
| 06 | `06_edgar_research_agent.py` | Custom research agent (skills mounted) |

**Talk line:** “generateContent forces you to own the agent loop. Interactions gives you state, background, and steps — so complex apps stay small.”

## Design.md / small stuff
For one-off design docs, a thin skill (`design-md`) is enough — same mount path as EDGAR. Don’t overbuild.

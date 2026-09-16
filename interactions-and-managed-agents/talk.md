# Builders Night — Legacy → Interactions → Agent Loop → Managed Agents

## Demo order (~30 min + Q&A)

Run `snippets/00_validate_setup.py` first if the API key isn't wired up.

### Act 1 — Legacy `generate_content` (why we moved on)

| # | Snippet | Pain point |
|---|---------|------------|
| 01 | `1_legacy_generate_content/01_chat_completions.py` | Manual history on every turn |
| 02 | `1_legacy_generate_content/02_thought_signatures.py` | Opaque `thought_signature` bytes to round-trip |
| 03 | `1_legacy_generate_content/03_multimodal_inputs.py` | Image bytes re-sent every turn |
| 04 | `1_legacy_generate_content/04_multimodal_fc.py` | Tool images trapped in base64 JSON |
| 05 | `1_legacy_generate_content/05_audio_generation.py` | Raw PCM + manual WAV header |

**Live pick (time-boxed):** 01 + 04, skip the rest.

**Line to land:** generateContent makes you own history, signatures, payloads, and schemas.

---

### Act 2 — Interactions API (same ideas, simpler surface)

| # | Snippet | What to land |
|---|---------|--------------|
| 01 | `2_interactions_api/01_hello_interaction.py` | Typed `steps` + `output_text` — no part hunting |
| 02 | `2_interactions_api/02_server_side_state.py` | `previous_interaction_id` — no history array |
| 03 | `2_interactions_api/03_background_async.py` | `background=True` — poll instead of blocking |
| 04 | `2_interactions_api/04_function_calling.py` | Tools are plain JSON dicts; one FC turn |
| 05 | `2_interactions_api/05_multimodal_input.py` | Raw video URI — print answer + `total_tokens` |
| 06 | `2_interactions_api/06_inbuilt_tools.py` | Same script, add `processing: "agentic"` — ~200× fewer tokens |

**Line to land:** Interactions gives you typed objects, server state, and built-in tools — often with less code.

---

### Act 3 — Building an agent (local)

Ported from [aie-workshop-2026-singapore](https://github.com/ivanleomk/aie-workshop-2026-singapore) steps 07–08.

| # | Snippet | What to land |
|---|---------|--------------|
| 01 | `3_building_an_agent/01_bash_agent.py` | Coding agent — bash only, runs on your machine |
| 02 | `3_building_an_agent/02_google_tools.py` | Same loop + built-in `google_search` / `url_context` |
| 03 | `3_building_an_agent/03_agentic_video.py` | Same loop + `agentic-video` skill; key in shell, not in prompt |

**Demo prompts:**
- 01: *"List all Python files in snippets/2_interactions_api"*
- 02: *"What's the weather in London?"*
- 03: *"Use the agentic-video skill to summarize the Gemini keynote YouTube link"*

**Line to land:** You own the loop and tools. Built-in Google tools drop in with one dict entry. Skills + shell env = custom capabilities without leaking secrets to the model.

---

### Act 4 — Managed agents (Google hosts the loop)

Progressive deploy ladder — each snippet adds one capability.

| # | Snippet | Add | Demo prompt |
|---|---------|-----|-------------|
| 00 | `4_managed_agent/00_quickstart.py` | Raw `stream=True` | What is 2+2? |
| 01 | `4_managed_agent/01_ids.py` | Last event → `id` + `environment_id` | What is 2+2? |
| 02 | `4_managed_agent/02_hn_crawl.py` | Pretty-print + code exec | Crawl HN — 10 stories |
| 03 | `4_managed_agent/03_google_tools.py` | `tools=[{"type": "google_search"}]` | Weather in SF |
| 04 | `4_managed_agent/04_environment_id.py` | Reuse `environment_id` | Write a UUID → `cat notes.txt` |
| 05 | `4_managed_agent/05_edgar_skill.py` | Mount `EdgarSkill` | What skills do you have? |
| 06 | `4_managed_agent/06_named_agents.py` | Deploy named agent via `client.agents.create` | What is your role and skills? |

**Line to land:** Act 3 loop + your SKILL.md + Google's sandbox and search = production agent. No loop maintenance, no tool-server infra.

> *"In Act 3, you host the loop and wire every tool. In Act 4, the managed agent ships with search, code execution, and a persistent environment — you just mount your SKILL."*

---

## Timing (~30 min)

| Act | ~min |
|-----|------|
| 1 Legacy (2 snippets live) | 4 |
| 2 Interactions (01, 02, 06 star) | 6 |
| 3 Local coding agent (01→03) | 7 |
| 4 Managed ladder | 10 |
| Q&A | 5 |

## What we do NOT cover tonight
- Harbor / Kaggle evals
- Deep OpenAlex (optional Q&A depth)
- Live Antigravity skill-tuning (skills are pre-built in `.agents/skills/` — Act 4 mounts them)

## Repo map for demos
- Skills: `.agents/skills/edgar-filings`, `research-brief`, `design-md`, …
- Snippets: `snippets/1_legacy_generate_content/` … `snippets/4_managed_agent/`
- Workshop source: [ivanleomk/aie-workshop-2026-singapore](https://github.com/ivanleomk/aie-workshop-2026-singapore)

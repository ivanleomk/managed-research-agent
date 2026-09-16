"""06 — Custom research agent. Mount repo skills; EDGAR brief in one call.

In AI Studio / Managed Agents: add this GitHub repo as an environment source
so `.agents/skills/edgar-filings` and `research-brief` auto-load.
"""
import time
from google import genai

client = genai.Client()

# Pseudocode shape for the talk — in Studio you mount the repo as a source.
# Via API, pass environment sources pointing at this repository.
PROMPT = """
Use the edgar-filings and research-brief skills.
Research NVIDIA (NVDA): find the latest 10-K, list Item 1A risk headings,
write out/brief-nvda-10k.md with citations. Do not invent numbers.
"""

interaction = client.interactions.create(
    agent="antigravity-preview-05-2026",
    environment="remote",  # + mount github.com/ivanleomk/managed-research-agent
    background=True,
    input=PROMPT,
)

while True:
    interaction = client.interactions.get(id=interaction.id)
    if interaction.status != "in_progress":
        break
    time.sleep(5)

print(interaction.output_text)

"""06 — Managed Agent: Deploy and call a Named Agent"""
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from lib.print import print_event, print_prompt

load_dotenv(override=True)
client = genai.Client()

AGENT_ID = "edgar-researcher"
SKILL_FILE = Path(__file__).resolve().parents[3] / ".agents/skills/EdgarSkill/SKILL.md"

# 1. Deploy the agent once — skills & instructions are baked into its definition
try:
    client.agents.delete(id=AGENT_ID)
except Exception:
    pass

agent = client.agents.create(
    id=AGENT_ID,
    base_agent="antigravity-preview-05-2026",
    description="Equity research analyst with SEC EDGAR filings skill.",
    system_instruction="You are an equity research analyst. Use your tools and skills to answer questions.",
    base_environment={
        "type": "remote",
        "sources": [{
            "type": "inline",
            "content": SKILL_FILE.read_text(),
            "target": ".agents/skills/EdgarSkill/SKILL.md",
        }],
    },
)
print(f"Deployed named agent: {agent.id}")

# 2. Invoke by name — callers don't need to mount skills or pass system instructions
PROMPT = "What is your role and what skills do you have?"
print_prompt(PROMPT)

stream = client.interactions.create(
    agent=AGENT_ID,
    environment="remote",
    stream=True,
    input=PROMPT,
)

for event in stream:
    print_event(event)

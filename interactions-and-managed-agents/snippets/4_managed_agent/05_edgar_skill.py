"""05 — Managed Agent: Mount EdgarSkill"""
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from lib.print import print_event, print_prompt

load_dotenv(override=True)
client = genai.Client()

SKILL_FILE = Path(__file__).resolve().parents[3] / ".agents/skills/EdgarSkill/SKILL.md"
SKILL_PATH = ".agents/skills/EdgarSkill/SKILL.md"
PROMPT = "What skills do you have?"

print_prompt(PROMPT)

stream = client.interactions.create(
    agent="antigravity-preview-05-2026",
    environment={
        "type": "remote",
        "sources": [{
            "type": "inline",
            "content": SKILL_FILE.read_text(),
            "target": SKILL_PATH,
        }],
    },
    stream=True,
    input=PROMPT,
)

for event in stream:
    print_event(event)

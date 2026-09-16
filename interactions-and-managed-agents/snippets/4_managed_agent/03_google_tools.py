"""03 — Managed Agent: Google Search"""

from dotenv import load_dotenv
from google import genai

from lib.print import print_event, print_prompt

load_dotenv(override=True)
client = genai.Client()

PROMPT = "What's the latest model from Google Deepmind"

print_prompt(PROMPT)

stream = client.interactions.create(
    agent="antigravity-preview-05-2026",
    environment="remote",
    stream=True,
    tools=[{"type": "google_search"}],
    input=PROMPT,
)

for event in stream:
    print_event(event)

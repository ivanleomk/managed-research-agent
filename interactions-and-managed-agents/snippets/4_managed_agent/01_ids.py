"""01 — Managed Agent: IDs on the completed event"""
from dotenv import load_dotenv
from google import genai
from rich import print

load_dotenv(override=True)
client = genai.Client()

stream = client.interactions.create(
    agent="antigravity-preview-05-2026",
    environment="remote",
    stream=True,
    input="What is 2+2?",
)

last = None
for event in stream:
    last = event

print(last)
print({"id": last.interaction.id, "environment_id": last.interaction.environment_id})
